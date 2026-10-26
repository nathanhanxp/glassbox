"""Time-aware layout. Documents sit on a date axis. Claims cluster around their sources."""

from datetime import date

NAMES = {
    "SCHW": "Schwab",
    "LPLA": "LPL",
    "RJF": "Raymond James",
    "AMP": "Ameriprise",
    "MS": "Morgan Stanley",
    "JPM": "JPMorgan",
    "USER": "Your note",
}
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _when(value: str | None) -> str:
    parsed = _parse(value)
    if not parsed:
        return ""
    return f"{MONTHS[parsed.month]} {parsed.day}, {parsed.year}"


def _doc_lines(doc: dict) -> tuple[str, str]:
    name = NAMES.get(doc["company"], doc["company"])
    kind = (doc.get("short_label") or doc["title"]).split("·")[0].strip()
    return f"{name} {kind}", _when(doc.get("published_at"))


COMPANY_Y = {
    "SCHW": 0,
    "LPLA": 120,
    "RJF": -120,
    "AMP": 240,
    "MS": -240,
    "JPM": 360,
    "USER": 480,
}
ORIGIN = date(2025, 10, 1)


def _parse(value: str | None) -> date | None:
    if not value:
        return None
    y, m, d = (int(p) for p in value.split("-"))
    return date(y, m, d)


def x_of(published: str | None) -> float:
    parsed = _parse(published)
    if not parsed:
        return 0.0
    days = (parsed - ORIGIN).days
    return (days - 190) * 1.35


def _on_or_before(published: str | None, as_of: str) -> bool:
    if not published:
        return False
    return published <= as_of


def build_graph(docs: list[dict], claims: list[dict], edges: list[dict], sentences: list[dict], as_of: str) -> dict:
    visible_docs = [
        d for d in docs
        if d.get("status") != "unavailable" and _on_or_before(d.get("published_at"), as_of)
    ]
    doc_ids = {d["id"] for d in visible_docs}
    visible_claims = [
        c for c in claims
        if c.get("doc_id") in doc_ids or c.get("scope") == "user_assertion" or _on_or_before(c.get("published_at"), as_of)
    ]
    # User assertions have no publication date and stay visible.
    visible_claims = [
        c for c in visible_claims
        if c.get("scope") == "user_assertion" or c.get("doc_id") in doc_ids
    ]
    cited_ids = {cid for sentence in sentences for cid in (sentence.get("claim_ids") or [])}
    visible_claims = [c for c in visible_claims if c["id"] in cited_ids]
    cited_docs = {c.get("doc_id") for c in visible_claims if c.get("doc_id")}
    visible_docs = [d for d in visible_docs if d["id"] in cited_docs]

    sentences_by_claim: dict[str, list[str]] = {}
    for sentence in sentences:
        for cid in sentence.get("claim_ids") or []:
            sentences_by_claim.setdefault(cid, []).append(sentence["id"])

    nodes = []
    per_doc_claims: dict[str, list[dict]] = {}
    for claim in visible_claims:
        per_doc_claims.setdefault(claim.get("doc_id") or "", []).append(claim)

    docs_sorted = sorted(visible_docs, key=lambda d: (d.get("published_at") or "", d["company"], d["id"]))
    doc_pos: dict[str, tuple[float, float, float]] = {}
    for index, doc in enumerate(docs_sorted):
        doc_pos[doc["id"]] = (index * 210, 0.0, 0.0)

    for doc in visible_docs:
        dx, dy, dz = doc_pos[doc["id"]]
        headline, when = _doc_lines(doc)
        nodes.append(
            {
                "id": doc["id"],
                "type": "document",
                "label": headline,
                "detail": when,
                "title": doc["title"],
                "company": doc["company"],
                "tier": doc["tier"],
                "date": doc.get("published_at"),
                "url": doc.get("url"),
                "date_origin": doc.get("date_origin"),
                "x": dx,
                "y": dy,
                "z": dz,
            }
        )

    for doc in visible_docs:
        dx, dy, dz = doc_pos[doc["id"]]
        group = per_doc_claims.get(doc["id"], [])
        for index, claim in enumerate(group):
            cited = sentences_by_claim.get(claim["id"], [])
            supported = True
            if cited:
                statuses = [s["status"] for s in sentences if s["id"] in cited]
                supported = all(status == "supported" for status in statuses) if statuses else True
            nodes.append(
                {
                    "id": claim["id"],
                    "type": "claim",
                    "label": claim.get("short_label") or "Claim",
                    "detail": _when(claim.get("published_at")),
                    "title": claim["text"],
                    "quote": claim.get("quote"),
                    "company": claim["company"],
                    "tier": claim["tier"],
                    "scope": claim["scope"],
                    "date": claim.get("published_at"),
                    "chunk_id": claim.get("chunk_id"),
                    "doc_id": claim.get("doc_id"),
                    "source_title": doc["title"],
                    "url": doc.get("url"),
                    "supported": supported and claim["tier"] != "secondary",
                    "secondary": claim["tier"] == "secondary",
                    "sentence_ids": cited,
                    "x": dx + ((index % 2) - 0.5) * 96,
                    "y": dy - 62 - (index // 2) * 54,
                    "z": (index % 3) * 28,
                }
            )

    for claim in visible_claims:
        if claim.get("scope") == "user_assertion":
            nodes.append(
                {
                    "id": claim["id"],
                    "type": "user_assertion",
                    "label": "Your note",
                    "detail": "Added in the report",
                    "title": claim["text"],
                    "quote": claim.get("quote") or "",
                    "company": "USER",
                    "tier": "user",
                    "date": claim.get("published_at"),
                    "supported": False,
                    "sentence_ids": sentences_by_claim.get(claim["id"], []),
                    "x": len(docs_sorted) * 210,
                    "y": -70,
                    "z": 40,
                }
            )

    node_ids = {n["id"] for n in nodes}
    links = []
    for edge in edges:
        if edge["src"] in node_ids and edge["dst"] in node_ids:
            links.append({"source": edge["src"], "target": edge["dst"], "type": edge["type"], "note": edge.get("note") or ""})
    for claim in visible_claims:
        num = f"num:{claim['id']}"
        if claim["id"] in node_ids and num in node_ids:
            links.append({"source": claim["id"], "target": num, "type": "supports", "note": ""})
    # Attach contradiction notes to the target claim so the sidebar can show the unresolved reading.
    notes: dict[str, list[str]] = {}
    for link in links:
        if link["type"] == "contradicts" and link.get("note"):
            notes.setdefault(link["target"], []).append(link["note"])
            notes.setdefault(link["source"], []).append(link["note"])
    for node in nodes:
        if node["id"] in notes:
            node["contradiction"] = notes[node["id"]][0]

    return {"as_of": as_of, "nodes": nodes, "links": links}
