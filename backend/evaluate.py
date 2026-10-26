"""Hand-labeled extraction, seeded-error catch rate, and a one-prompt baseline.

Run from backend/:  python evaluate.py
"""

import json
import time
from pathlib import Path

from app.checks import SEEDED_ERRORS, check_sentence, code_passed, failed
from app.chunking import chunk_document
from app.corpus import DOCUMENTS
from app.finance import scenario
from app.pipeline import extract, link

GOLD = [
    {"doc": "schw-q3-2026-release", "quote": "ended September at $492.8 billion", "label": "September sweep level"},
    {"doc": "schw-q3-2026-release", "quote": "Net interest margin expanded quarter-over-quarter to 3.04%", "label": "NIM"},
    {"doc": "schw-q3-2026-release", "quote": "to a record $7.2 billion", "label": "Q3 revenue"},
    {"doc": "schw-q3-2026-release", "quote": "short credits totaled $63.3 billion", "label": "September short credits"},
    {"doc": "schw-q3-2026-release", "quote": "Transactional sweep cash includes bank sweep deposits", "label": "Sweep definition"},
    {"doc": "schw-q3-2026-release", "quote": "Introduced Charley", "label": "Charley in the release"},
    {"doc": "schw-q3-2026-release", "quote": "Schwab money market funds $699,067", "label": "Money funds as printed"},
    {"doc": "schw-q3-2026-call", "quote": "finished the quarter at $492.8 billion", "label": "Call sweep level"},
    {"doc": "schw-q3-2026-call", "quote": "cash go back into the market", "label": "Reinvestment"},
    {"doc": "schw-q3-2026-call", "quote": "fueled by the activity in IPOs", "label": "IPOs"},
    {"doc": "schw-q3-2026-call", "quote": "this is not cash sorting", "label": "Not cash sorting"},
    {"doc": "schw-q3-2026-call", "quote": "introduced Charlie", "label": "Charlie on the call"},
    {"doc": "schw-q3-2026-call", "quote": "77% of U.S. investors use AI today", "label": "77% / 90%"},
    {"doc": "schw-q3-2026-call", "quote": "blocking unauthorized agents", "label": "Agent guardrails"},
    {"doc": "schw-q3-2026-call", "quote": "holds more cash than other active traders", "label": "AI traders hold more cash"},
    {"doc": "schw-q3-2026-call", "quote": "doubled in about the last six months", "label": "LLM links doubled"},
    {"doc": "schw-q3-2026-call", "quote": "25% more productive", "label": "Developer productivity"},
    {"doc": "schw-q3-2026-call", "quote": "yielding sub 2%", "label": "Sub-2% securities book"},
    {"doc": "schw-q2-2026-release", "quote": "ended June at $485.7 billion", "label": "June sweep"},
    {"doc": "schw-q2-2026-release", "quote": "short cash credits equaling $42.1 billion and $43.7 billion", "label": "June short credits"},
    {"doc": "schw-q2-2026-release", "quote": "Portfolio Insights", "label": "Q2 AI product"},
    {"doc": "schw-10q-2026-q2", "quote": "increased by a total of $42.7 billion", "label": "10-Q sweep deposits"},
    {"doc": "schw-aug-2026-monthly", "quote": "end August at $483.3 billion", "label": "August sweep"},
    {"doc": "schw-q3-2025-release", "quote": "ended September at $425.6 billion", "label": "2025 sweep"},
    {"doc": "schw-q3-2025-release", "quote": "declined by $12.9 billion", "label": "2025 funding paydown"},
    {"doc": "lpl-q2-2026", "quote": "Total client cash balances were $57 billion", "label": "LPL cash"},
    {"doc": "lpl-q2-2026", "quote": "were 2.2%", "label": "LPL cash ratio"},
    {"doc": "rjf-q3-2026-call", "quote": "ended the quarter at $58.8 billion", "label": "RJF sweep"},
    {"doc": "amp-q2-2026", "quote": "Cash sweep balances were $28.8 billion", "label": "Ameriprise sweep"},
    {"doc": "ms-q3-2026", "quote": "higher average sweep deposits", "label": "Morgan Stanley sweep deposits"},
    {"doc": "news-aardvark", "quote": "($12.5B)", "label": "Analyst $12.5B reading"},
    {"doc": "news-tradeflock", "quote": "fell about $12.5 billion", "label": "TradeFlock estimate"},
    {"doc": "schw-q3-2026-call", "quote": "connecting their LLMs to Schwab", "label": "LLM connections"},
    {"doc": "schw-q3-2026-call", "quote": "leads to more cash held by those clients", "label": "Engagement and cash"},
    {"doc": "schw-q3-2026-call", "quote": "it will impact cash levels", "label": "Fear that AI cuts cash"},
    {"doc": "schw-q3-2026-call", "quote": "the more cash they hold", "label": "Opposite of the AI fear"},
    {"doc": "schw-q2-2026-release", "quote": "revenue growth of 21%", "label": "Q2 revenue"},
    {"doc": "schw-q3-2025-release", "quote": "grew by $13.5 billion versus 2Q25", "label": "2025 CFO on funding"},
    {"doc": "rjf-q3-2026-call", "quote": "proprietary AI assistant", "label": "Raymond assistant"},
    {"doc": "amp-q2-2026", "quote": "including our AI capabilities", "label": "Ameriprise AI spend"},
    {"doc": "amp-q1-2026", "quote": "stable at $29.4 billion", "label": "Ameriprise Q1 sweep"},
    {"doc": "ms-q3-2026", "quote": "record net revenues of $9.1 billion", "label": "MS wealth revenue"},
    {"doc": "ms-q2-2026", "quote": "higher average sweep deposits and the cumulative impact", "label": "MS Q2 sweep deposits"},
    {"doc": "jpm-q3-2026", "quote": "client investment assets up 15%", "label": "JPM client assets"},
    {"doc": "jpm-q2-2026", "quote": "client investment assets up 21%", "label": "JPM Q2 client assets"},
    {"doc": "jpm-q2-2026", "quote": "first-time investors of nearly 44,000", "label": "JPM new investors"},
    {"doc": "news-aardvark", "quote": "framed around AI agents", "label": "Analyst frames the AI debate"},
    {"doc": "news-aardvark", "quote": "hold more cash, not less", "label": "Analyst on AI cash"},
    {"doc": "news-tradeflock", "quote": "up $7.1 billion from June", "label": "TradeFlock restates the release"},
    {"doc": "news-tradeflock", "quote": "this is not cash sorting in any way", "label": "TradeFlock quotes the call"},
    {"doc": "schw-q3-2026-call", "quote": "cannot be underestimated", "label": "People and technology", "expect_miss": True},
]

# Real lines the sentence rule does not keep, plus the derived figure, which is not a source sentence.
MISSES = [
    {
        "label": "People-and-technology line on the call",
        "quote": "That combination of people and technology has always been central to Schwab and cannot be underestimated.",
        "why": "No figure and no cash, sweep, or agent keyword, so the code filter never emits it.",
    },
    {
        "label": "Sweep cash excluding short credits fell $12.5 billion, as a Schwab sentence",
        "quote": "sweep cash excluding short credits fell $12.5 billion",
        "why": "Schwab does not say this. The finance tab recomputes it from the June and September releases. Extraction correctly does not invent it.",
    },
]


def _hit(claims: list[dict], item: dict) -> bool:
    return any(c["doc_id"] == item["doc"] and item["quote"] in c["quote"] for c in claims)


def _bind(claims: list[dict], doc_id: str, snippet: str) -> str | None:
    for claim in claims:
        if claim["doc_id"] == doc_id and snippet in claim["quote"]:
            return claim["id"]
    return None


BINDS = {
    "e-month": ("schw-q3-2026-release", "ended September at $492.8"),
    "e-subset": ("schw-q3-2026-release", "short credits totaled $63.3"),
    "e-peer": ("lpl-q2-2026", "were 2.2%"),
    "e-misquote": ("schw-q3-2026-release", "ended September at $492.8"),
    "e-after": ("schw-q3-2026-release", "ended September at $492.8"),
    "e-tolerance": ("schw-q3-2026-release", "ended September at $492.8"),
    "e-rjf": ("rjf-q3-2026-call", "$58.8 billion"),
    "e-not-in-source": ("schw-q3-2026-call", "not cash sorting"),
    "e-direction": ("schw-q3-2026-release", "ended September at $492.8"),
    "e-ai-flip": ("schw-q3-2026-call", "holds more cash"),
    "e-hedge": ("news-aardvark", "($12.5B)"),
    "e-entail": ("schw-q3-2026-call", "not cash sorting"),
}


def main() -> None:
    docs = [d for d in DOCUMENTS if d.get("text")]
    chunks = []
    for doc in docs:
        chunks.extend(chunk_document(doc))
    started = time.perf_counter()
    claims = extract(docs, chunks)
    edges = link(claims, docs)
    elapsed = time.perf_counter() - started

    hits = [item for item in GOLD if not item.get("expect_miss") and _hit(claims, item)]
    missed = [item for item in GOLD if not item.get("expect_miss") and not _hit(claims, item)]
    expected_misses = [item for item in GOLD if item.get("expect_miss")]
    unexpected_hits = [item for item in expected_misses if _hit(claims, item)]
    gold_quotes = {(item["doc"], item["quote"]) for item in GOLD if not item.get("expect_miss")}
    extras = [
        c for c in claims
        if not any(c["doc_id"] == doc and quote in c["quote"] for doc, quote in gold_quotes)
    ]
    precision = len(hits) / (len(hits) + len(extras)) if (hits or extras) else 0
    recall = len(hits) / (len(GOLD) - len(expected_misses)) if GOLD else 0

    docs_by_id = {d["id"]: d for d in docs}
    chunks_by_id = {c["id"]: c for c in chunks}
    claims_by_id = {c["id"]: c for c in claims}

    caught = []
    slipped = []
    for error in SEEDED_ERRORS:
        doc_id, snippet = BINDS[error["id"]]
        claim_id = _bind(claims, doc_id, snippet)
        sentence = dict(error)
        sentence["claim_ids"] = [claim_id] if claim_id else ["missing"]
        as_of = error.get("as_of") or "2026-10-26"
        checks = check_sentence(sentence, claims=claims_by_id, docs=docs_by_id, chunks=chunks_by_id, as_of=as_of)
        names = [c["name"] for c in failed(checks)]
        row = {"id": error["id"], "label": error["label"], "failed_checks": names, "needs_nim": error.get("needs_nim", False)}
        if error.get("needs_nim"):
            if code_passed(checks):
                slipped.append({**row, "why": "Code checks pass. This one needs the NIM entailment pass. Without a key it is not caught."})
            else:
                caught.append(row)
        elif names:
            caught.append(row)
        else:
            slipped.append({**row, "why": "No code check failed."})

    # Baseline: one prompt, no code checks. The seeded errors are the sort of sentence that ships.
    baseline_sentences = len(SEEDED_ERRORS)
    baseline_unsupported_if_checked = len(caught)
    baseline_prompt_tokens = sum(len(d["text"]) for d in docs) // 4

    finance = scenario("2026-10-26")
    report = {
        "extraction": {
            "labeled": len(GOLD) - len(expected_misses),
            "hit": len(hits),
            "missed_labels": [m["label"] for m in missed],
            "expected_misses_still_missing": [m["label"] for m in expected_misses if not _hit(claims, m)],
            "expected_misses_that_were_extracted": [m["label"] for m in unexpected_hits],
            "intentional_structural_misses": MISSES,
            "unlabeled_extras": [{"doc": c["doc_id"], "quote": c["quote"][:180]} for c in extras],
            "precision_against_labels": round(precision, 3),
            "recall_against_labels": round(recall, 3),
            "claims": len(claims),
            "edges": len(edges),
            "chunks": len(chunks),
            "extract_seconds": round(elapsed, 3),
        },
        "seeded_errors": {
            "planted": len(SEEDED_ERRORS),
            "caught_by_code": len(caught),
            "not_caught": slipped,
            "catch_rate_including_nim_gap": round(len(caught) / len(SEEDED_ERRORS), 3),
            "detail": caught,
        },
        "baseline_versus_pipeline": {
            "note": "No model was called. Latency of a live one-prompt baseline was not measured.",
            "pipeline_llm_calls_in_this_script": 0,
            "pipeline_code_latency_seconds": round(elapsed, 3),
            "baseline_shape": "one prompt over the whole cache, no code checks before the answer",
            "baseline_prompt_tokens_estimate": baseline_prompt_tokens,
            "baseline_seeded_errors_that_would_ship": baseline_sentences - 0,
            "same_errors_caught_once_the_verifier_runs": baseline_unsupported_if_checked,
            "tradeoff": "A one-prompt baseline is one call. It does not run the six code checks, so the seeded errors ship. The pipeline's catch rate is the code checks. Speed without those checks is a real tradeoff, not a win.",
        },
        "finance_recompute_billion": None if not finance.get("recompute") else finance["recompute"]["decline_billion"],
    }
    out = Path(__file__).resolve().parent / "data" / "evaluation.json"
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
