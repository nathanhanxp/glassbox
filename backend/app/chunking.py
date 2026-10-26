"""Chunk at about 400 tokens. Ids stay put for a given document."""

def chunk_document(doc: dict) -> list[dict]:
    if doc.get("status") == "unavailable" or not (doc.get("text") or "").strip():
        return []
    paras = [p.strip() for p in doc["text"].split("\n") if p.strip()]
    chunks: list[dict] = []
    buf: list[str] = []
    words = 0

    def flush() -> None:
        nonlocal buf, words
        if not buf:
            return
        chunks.append(
            {
                "id": f"{doc['id']}:c{len(chunks):02d}",
                "document_id": doc["id"],
                "text": "\n".join(buf),
            }
        )
        buf = []
        words = 0

    for para in paras:
        count = len(para.split())
        if words and words + count > 300:
            flush()
        buf.append(para)
        words += count
    flush()
    return chunks
