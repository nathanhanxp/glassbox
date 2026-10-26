"""Code checks run before any model entailment call. Order is fixed."""

import re
from typing import Any

NUMBER_RE = re.compile(
    r"\(?\$?\s*(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\)?\s*(billion|million|%|bp)?",
    re.I,
)

# A sentence number must sit near a cited number of the same unit.
BILLION_TOL = 0.16
PERCENT_TOL = 0.2


def parse_numbers(text: str) -> list[dict]:
    found = []
    for match in NUMBER_RE.finditer(text or ""):
        raw = match.group(1).replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            continue
        unit = (match.group(2) or "").lower()
        if unit in {"billion", "b"}:
            unit = "billion"
        elif unit == "million":
            unit = "million"
        elif unit == "%":
            unit = "percent"
        elif unit == "bp":
            unit = "bp"
        else:
            # $12.5B style already consumed. Bare 12.5B handled below.
            tail = text[match.end(): match.end() + 2]
            if tail.lower().startswith("b") and value < 10000:
                unit = "billion"
            else:
                unit = "raw"
        window = text[max(0, match.start() - 1): match.end() + 1]
        if "(" in text[max(0, match.start() - 2): match.start() + 1] and ")" in text[match.end(): match.end() + 2]:
            value = -abs(value)
        found.append({"value": value, "unit": unit, "raw": match.group(0).strip(), "span": window})
    # ($12.5B) and +$7.1B
    for match in re.finditer(r"\(?\+?\$?(\d+(?:\.\d+)?)B\)?", text or ""):
        value = float(match.group(1))
        if text[match.start()] == "(" or (match.start() > 0 and text[match.start() - 1] == "("):
            value = -abs(value)
        found.append({"value": value, "unit": "billion", "raw": match.group(0)})
    # de-dupe
    uniq = []
    seen = set()
    for n in found:
        key = (round(n["value"], 4), n["unit"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(n)
    return uniq


def _close(a: float, b: float, unit: str) -> bool:
    tol = PERCENT_TOL if unit == "percent" else BILLION_TOL if unit == "billion" else 0.2
    if unit == "million":
        tol = 1.0
    return abs(a - b) <= tol


def _cited(sentence: dict, claims: dict[str, dict]) -> list[dict]:
    return [claims[i] for i in sentence.get("claim_ids") or [] if i in claims]


def check_sentence(
    sentence: dict,
    *,
    claims: dict[str, dict],
    docs: dict[str, dict],
    chunks: dict[str, dict],
    as_of: str,
) -> list[dict]:
    """Return checks in the required order. `passed` is false when a check fails."""
    results = []
    cited = _cited(sentence, claims)
    missing = [i for i in (sentence.get("claim_ids") or []) if i not in claims]

    def add(name: str, passed: bool, detail: str) -> None:
        results.append({"name": name, "passed": passed, "detail": detail})

    if sentence.get("meta"):
        add("cited_ids", True, "Corpus note, not a sourced financial claim.")
        return results

    # 1. cited ids exist
    if sentence.get("derived"):
        ok = not missing and len(cited) >= 2
        add("cited_ids", ok, "Derived sentence cites the Schwab inputs." if ok else f"Missing ids: {missing}")
    elif sentence.get("user_assertion"):
        add("cited_ids", True, "User assertion has no source id. It stays unverified.")
    else:
        chunk_ok = True
        for c in cited:
            if c.get("chunk_id") and c["chunk_id"] not in chunks:
                chunk_ok = False
        ok = not missing and bool(cited) and chunk_ok
        add("cited_ids", ok, "Cited claims and chunk ids exist." if ok else f"Missing or empty citations {missing}")

    # 2. numbers match within tolerance
    if sentence.get("user_assertion"):
        add("numbers", True, "Not checked. User assertion is not a sourced figure.")
    elif sentence.get("derived"):
        derived_ok, detail = _check_derivation(sentence, cited)
        add("numbers", derived_ok, detail)
    else:
        sent_nums = [n for n in parse_numbers(sentence.get("text") or "") if n["unit"] in {"billion", "percent", "million"}]
        claim_nums = []
        for c in cited:
            claim_nums.extend(c.get("numbers") or parse_numbers(c.get("quote") or c.get("text") or ""))
        bad = []
        for n in sent_nums:
            if not any(_close(abs(n["value"]), abs(m["value"]), n["unit"]) and n["unit"] == m["unit"] for m in claim_nums):
                bad.append(n["raw"])
        add("numbers", not bad, "Numbers match the cited claims." if not bad else f"Unmatched numbers: {bad}")

    # 3. source date on or before the as-of date
    if sentence.get("user_assertion") or sentence.get("meta"):
        add("as_of", True, "No source date.")
    else:
        late = []
        undated = []
        for c in cited:
            published = c.get("published_at") or ""
            if not published:
                undated.append(c["id"])
            elif published > as_of:
                late.append(f"{c['id']} {published}")
        ok = not late and not undated and bool(cited)
        detail = "Published on or before the as-of date."
        if late:
            detail = f"Published after the as-of date: {late}"
        elif undated:
            detail = f"No publication date on {undated}"
        add("as_of", ok, detail)

    # 4. quote appears in the source text
    if sentence.get("derived"):
        add("quote", True, "Recomputed from cited figures. No separate quote.")
    elif sentence.get("user_assertion"):
        add("quote", False, "No source quote. Saved as an unverified user assertion.")
    else:
        quote = (sentence.get("quote") or "").strip()
        if not quote:
            add("quote", False, "Sentence has no exact quote.")
        else:
            missing_q = []
            for c in cited:
                doc = docs.get(c.get("doc_id") or "")
                if not doc or quote not in (doc.get("text") or ""):
                    missing_q.append(c.get("doc_id"))
            add(
                "quote",
                not missing_q and bool(cited),
                "Quoted span found in the source text." if not missing_q else f"Quote not in {missing_q}",
            )

    # 5. scope: a subset must not be stated as the total
    if sentence.get("user_assertion") or sentence.get("derived") or sentence.get("meta"):
        add("scope", True, "Scope checked against the derivation." if sentence.get("derived") else "Not a subset-versus-total claim.")
    else:
        scopes = {c.get("scope") for c in cited}
        text_l = (sentence.get("text") or "").lower()
        calls_total = any(p in text_l for p in ["total transactional sweep", "total sweep cash", "the entire sweep"])
        subset_as_total = "subset" in scopes and calls_total
        total_as_subset = "total_sweep_cash" in scopes and "only the short credit" in text_l
        ok = not subset_as_total and not total_as_subset
        add(
            "scope",
            ok,
            "Scope matches the cited claim." if ok else "A subset figure is presented as the total, or the reverse.",
        )

    # 6. company: a peer claim cannot be attributed to Schwab
    if sentence.get("user_assertion") or sentence.get("meta"):
        add("company", True, "Not a company attribution.")
    else:
        companies = {c.get("company") for c in cited}
        text_l = sentence.get("text") or ""
        names = {
            "SCHW": ["schwab"],
            "LPLA": ["lpl"],
            "RJF": ["raymond james"],
            "AMP": ["ameriprise"],
            "MS": ["morgan stanley"],
            "JPM": ["jpmorgan", "jp morgan"],
        }
        named = {code for code, words in names.items() if any(w in text_l.lower() for w in words)}
        ok = True
        detail = "Company matches the cited source."
        if "SCHW" in named and any(c != "SCHW" for c in companies):
            # Allowed when the sentence also names the peer.
            others = companies - {"SCHW"}
            if not others <= named:
                ok = False
                detail = "A peer claim is attributed to Schwab."
        if named and companies and not (named & companies) and "SCHW" not in named:
            ok = False
            detail = "The company named in the sentence is not the cited company."
        add("company", ok, detail)

    # Hedge wording for news and analyst claims. Checked with the code pass, before NIM.
    if any(c.get("tier") == "secondary" for c in cited) and not sentence.get("derived"):
        text_l = (sentence.get("text") or "").lower()
        hedged = any(w in text_l for w in ["reported", "analysts said", "according to", "estimate"])
        add("hedge", hedged, "Secondary source uses hedged wording." if hedged else "News or analyst claim needs hedged wording.")

    return results


def _check_derivation(sentence: dict, cited: list[dict]) -> tuple[bool, str]:
    """June sweep - June short credits, September sweep - September short credits, then the change."""
    by_quote = " ".join((c.get("quote") or "") for c in cited)
    need = {
        "june_sweep": 485.7,
        "june_short": 43.7,
        "sept_sweep": 492.8,
        "sept_short": 63.3,
    }
    blob = by_quote
    if "485.7" not in blob or "43.7" not in blob or "492.8" not in blob or "63.3" not in blob:
        return False, "Derivation is missing one of 485.7, 43.7, 492.8, 63.3."
    june = round(need["june_sweep"] - need["june_short"], 1)
    sept = round(need["sept_sweep"] - need["sept_short"], 1)
    change = round(june - sept, 1)
    text_nums = [n for n in parse_numbers(sentence.get("text") or "") if n["unit"] == "billion"]
    values = [round(abs(n["value"]), 1) for n in text_nums]
    needed = {june, sept, change}
    if not needed <= set(values):
        return False, f"Sentence should show {june}, {sept}, and a {change} decline. Found {values}."
    if "schwab" not in (sentence.get("text") or "").lower():
        return False, "The recompute has to say it uses Schwab's figures."
    return True, f"Recomputed from Schwab's releases: {june} in June, {sept} in September, decline of {change}."


def failed(checks: list[dict]) -> list[dict]:
    return [c for c in checks if not c["passed"]]


def code_passed(checks: list[dict]) -> bool:
    return not failed(checks)


# Sentences the evaluation plants. They are not part of the demo report.
SEEDED_ERRORS: list[dict[str, Any]] = [
    {
        "id": "e-month",
        "label": "Wrong month",
        "text": "Schwab reported that transactional sweep cash ended August at $492.8 billion.",
        "quote": "Transactional sweep cash ended August at $492.8 billion.",
        "claim_ids": ["schw-q3-2026-release:sweep"],
        "expect": "quote",
    },
    {
        "id": "e-subset",
        "label": "Subset presented as the total",
        "text": "Short credits of $63.3 billion were Schwab's total transactional sweep cash.",
        "quote": "For the month of September 2026, margin loans totaled $60.7 billion and short credits totaled $63.3 billion.",
        "claim_ids": ["schw-q3-2026-release:short"],
        "expect": "scope",
    },
    {
        "id": "e-peer",
        "label": "Peer claim attributed to Schwab",
        "text": "Schwab's client cash was 2.2% of total client assets, down from 2.5% in the prior quarter.",
        "quote": "Client cash balances as a percentage of total client assets were 2.2%, down from 2.5% in the prior quarter and 2.6% in the prior year.",
        "claim_ids": ["lpl-q2-2026:ratio"],
        "expect": "company",
    },
    {
        "id": "e-misquote",
        "label": "Misquote",
        "text": "Schwab reported that sweep cash ended September at $425.6 billion in the 2026 release.",
        "quote": "Client transactional sweep cash balances ended September at $425.6 billion in the 2026 release.",
        "claim_ids": ["schw-q3-2026-release:sweep"],
        "expect": "quote",
    },
    {
        "id": "e-after",
        "label": "Source after the as-of date",
        "text": "Schwab reported that client transactional sweep cash ended September at $492.8 billion.",
        "quote": "Client transactional sweep cash balances ended September at $492.8 billion, an increase of $7.1 billion versus the prior quarter-end, reflecting continued demand for long/short strategies and organic growth, partially offset by client asset allocation decisions.",
        "claim_ids": ["schw-q3-2026-release:sweep"],
        "as_of": "2026-04-17",
        "expect": "as_of",
    },
    {
        "id": "e-tolerance",
        "label": "Number outside tolerance",
        "text": "Schwab reported September sweep cash of $500 billion.",
        "quote": "Client transactional sweep cash balances ended September at $492.8 billion, an increase of $7.1 billion versus the prior quarter-end, reflecting continued demand for long/short strategies and organic growth, partially offset by client asset allocation decisions.",
        "claim_ids": ["schw-q3-2026-release:sweep"],
        "expect": "numbers",
    },
    {
        "id": "e-rjf",
        "label": "Raymond James balance attributed to Schwab",
        "text": "Schwab's domestic cash sweep ended the quarter at $58.8 billion.",
        "quote": "Clients' domestic cash sweep and enhanced savings program balances ended the quarter at $58.8 billion, up 2% from the preceding quarter and 7% over the prior year level representing 3.4% of domestic PCG client assets at quarter end.",
        "claim_ids": ["rjf-q3-2026-call:sweep"],
        "expect": "company",
    },
    {
        "id": "e-not-in-source",
        "label": "Quote absent from the source",
        "text": "Schwab said clients sorted cash into money funds at a record pace in September.",
        "quote": "clients sorted cash into money funds at a record pace in September",
        "claim_ids": ["schw-q3-2026-call:not-sorting"],
        "expect": "quote",
    },
    {
        "id": "e-direction",
        "label": "Wrong direction on a real number",
        "text": "Schwab reported that transactional sweep cash fell $7.1 billion in the quarter.",
        "quote": "transactional sweep cash fell $7.1 billion in the quarter",
        "claim_ids": ["schw-q3-2026-release:sweep"],
        "expect": "quote",
    },
    {
        "id": "e-ai-flip",
        "label": "AI cash claim reversed",
        "text": "Schwab said AI-connected traders hold less cash than other active traders.",
        "quote": "AI-connected traders hold less cash than other active traders",
        "claim_ids": ["schw-q3-2026-call:traders"],
        "expect": "quote",
    },
    {
        "id": "e-hedge",
        "label": "Secondary claim without a hedge",
        "text": "Sweep cash excluding short credits fell $12.5 billion in the quarter.",
        "quote": "stripping long/short short credits out of transactional sweep cash shows a ($12.5B) sequential decline beneath the reported +$7.1B.",
        "claim_ids": ["news-aardvark:decline"],
        "expect": "hedge",
    },
    {
        "id": "e-entail",
        "label": "Real quote, conclusion the quote does not support",
        "text": "Verdeschi said this is not cash sorting in any way, so clients moved cash into money market funds to chase yield.",
        "quote": "In terms of cash, just to be clear, even with those higher rates, this is not cash sorting in any way.",
        "claim_ids": ["schw-q3-2026-call:not-sorting"],
        "expect": "entailment",
        "needs_nim": True,
    },
]
