"""SQLite storage for documents, claims, edges, sentences, and the event log."""

import json
import sqlite3
import threading
from typing import Any

from .config import DB_PATH

_lock = threading.Lock()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init() -> None:
    with _lock, connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
              id TEXT PRIMARY KEY,
              title TEXT,
              question TEXT,
              as_of TEXT,
              status TEXT,
              created_at TEXT,
              report_json TEXT,
              metrics_json TEXT,
              gaps_json TEXT
            );
            CREATE TABLE IF NOT EXISTS documents (
              id TEXT,
              run_id TEXT,
              job TEXT,
              url TEXT,
              title TEXT,
              published_at TEXT,
              tier TEXT,
              company TEXT,
              content_hash TEXT,
              text TEXT,
              status TEXT,
              source_kind TEXT,
              date_origin TEXT,
              short_label TEXT,
              PRIMARY KEY (run_id, id)
            );
            CREATE TABLE IF NOT EXISTS chunks (
              id TEXT,
              run_id TEXT,
              document_id TEXT,
              text TEXT,
              PRIMARY KEY (run_id, id)
            );
            CREATE TABLE IF NOT EXISTS claims (
              id TEXT,
              run_id TEXT,
              text TEXT,
              quote TEXT,
              chunk_id TEXT,
              doc_id TEXT,
              company TEXT,
              tier TEXT,
              published_at TEXT,
              scope TEXT,
              event_type TEXT,
              numbers_json TEXT,
              short_label TEXT,
              PRIMARY KEY (run_id, id)
            );
            CREATE TABLE IF NOT EXISTS edges (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT,
              src TEXT,
              dst TEXT,
              type TEXT,
              note TEXT
            );
            CREATE TABLE IF NOT EXISTS sentences (
              id TEXT,
              run_id TEXT,
              text TEXT,
              quote TEXT,
              claim_ids TEXT,
              status TEXT,
              checks_json TEXT,
              attempt INTEGER,
              hedged INTEGER,
              derived INTEGER,
              PRIMARY KEY (run_id, id)
            );
            CREATE TABLE IF NOT EXISTS events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT,
              ts TEXT,
              agent TEXT,
              kind TEXT,
              message TEXT,
              payload_json TEXT
            );
            CREATE TABLE IF NOT EXISTS corrections (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT,
              text TEXT,
              created_at TEXT
            );
            """
        )


def _write(sql: str, args: tuple = ()) -> None:
    with _lock, connect() as conn:
        conn.execute(sql, args)


def _many(sql: str, rows: list[tuple]) -> None:
    with _lock, connect() as conn:
        conn.executemany(sql, rows)


def query(sql: str, args: tuple = ()) -> list[dict]:
    with _lock, connect() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def insert_run(row: dict) -> None:
    _write(
        """INSERT INTO runs (id, title, question, as_of, status, created_at, report_json, metrics_json, gaps_json)
           VALUES (:id, :title, :question, :as_of, :status, :created_at, :report_json, :metrics_json, :gaps_json)""",
        row,
    )


def update_run(run_id: str, **fields: Any) -> None:
    cols = ", ".join(f"{k} = ?" for k in fields)
    _write(f"UPDATE runs SET {cols} WHERE id = ?", (*fields.values(), run_id))


def list_runs() -> list[dict]:
    return query("SELECT id, title, question, as_of, status, created_at, metrics_json, gaps_json FROM runs ORDER BY created_at DESC")


def get_run(run_id: str) -> dict | None:
    rows = query("SELECT * FROM runs WHERE id = ?", (run_id,))
    return rows[0] if rows else None


def replace_documents(run_id: str, docs: list[dict]) -> None:
    with _lock, connect() as conn:
        conn.execute("DELETE FROM documents WHERE run_id = ?", (run_id,))
        conn.executemany(
            """INSERT INTO documents
               (id, run_id, job, url, title, published_at, tier, company, content_hash, text, status, source_kind, date_origin, short_label)
               VALUES (:id, :run_id, :job, :url, :title, :published_at, :tier, :company, :content_hash, :text, :status, :source_kind, :date_origin, :short_label)""",
            [{**d, "run_id": run_id} for d in docs],
        )


def replace_chunks(run_id: str, chunks: list[dict]) -> None:
    with _lock, connect() as conn:
        conn.execute("DELETE FROM chunks WHERE run_id = ?", (run_id,))
        conn.executemany(
            "INSERT INTO chunks (id, run_id, document_id, text) VALUES (:id, :run_id, :document_id, :text)",
            [{**c, "run_id": run_id} for c in chunks],
        )


def replace_claims(run_id: str, claims: list[dict]) -> None:
    with _lock, connect() as conn:
        conn.execute("DELETE FROM claims WHERE run_id = ?", (run_id,))
        conn.executemany(
            """INSERT INTO claims
               (id, run_id, text, quote, chunk_id, doc_id, company, tier, published_at, scope, event_type, numbers_json, short_label)
               VALUES (:id, :run_id, :text, :quote, :chunk_id, :doc_id, :company, :tier, :published_at, :scope, :event_type, :numbers_json, :short_label)""",
            [
                {
                    **c,
                    "run_id": run_id,
                    "numbers_json": json.dumps(c.get("numbers") or []),
                }
                for c in claims
            ],
        )


def add_claim(run_id: str, claim: dict) -> None:
    row = {
        **claim,
        "run_id": run_id,
        "numbers_json": json.dumps(claim.get("numbers") or []),
    }
    with _lock, connect() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO claims
               (id, run_id, text, quote, chunk_id, doc_id, company, tier, published_at, scope, event_type, numbers_json, short_label)
               VALUES (:id, :run_id, :text, :quote, :chunk_id, :doc_id, :company, :tier, :published_at, :scope, :event_type, :numbers_json, :short_label)""",
            row,
        )


def replace_edges(run_id: str, edges: list[dict]) -> None:
    with _lock, connect() as conn:
        conn.execute("DELETE FROM edges WHERE run_id = ?", (run_id,))
        conn.executemany(
            "INSERT INTO edges (run_id, src, dst, type, note) VALUES (?, ?, ?, ?, ?)",
            [(run_id, e["src"], e["dst"], e["type"], e.get("note") or "") for e in edges],
        )


def replace_sentences(run_id: str, sentences: list[dict]) -> None:
    with _lock, connect() as conn:
        conn.execute("DELETE FROM sentences WHERE run_id = ?", (run_id,))
        conn.executemany(
            """INSERT INTO sentences (id, run_id, text, quote, claim_ids, status, checks_json, attempt, hedged, derived)
               VALUES (:id, :run_id, :text, :quote, :claim_ids, :status, :checks_json, :attempt, :hedged, :derived)""",
            [
                {
                    "id": s["id"],
                    "run_id": run_id,
                    "text": s["text"],
                    "quote": s.get("quote") or "",
                    "claim_ids": json.dumps(s.get("claim_ids") or []),
                    "status": s["status"],
                    "checks_json": json.dumps(s.get("checks") or []),
                    "attempt": s.get("attempt") or 1,
                    "hedged": 1 if s.get("hedged") else 0,
                    "derived": 1 if s.get("derived") else 0,
                }
                for s in sentences
            ],
        )


def add_event(run_id: str, ts: str, agent: str, kind: str, message: str, payload: dict) -> int:
    with _lock, connect() as conn:
        cur = conn.execute(
            "INSERT INTO events (run_id, ts, agent, kind, message, payload_json) VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, ts, agent, kind, message, json.dumps(payload)),
        )
        return int(cur.lastrowid)


def events_for(run_id: str) -> list[dict]:
    rows = query(
        "SELECT id, run_id, ts, agent, kind, message, payload_json FROM events WHERE run_id = ? ORDER BY id",
        (run_id,),
    )
    for r in rows:
        r["payload"] = json.loads(r.pop("payload_json") or "{}")
    return rows


def docs_for(run_id: str) -> list[dict]:
    return query("SELECT * FROM documents WHERE run_id = ?", (run_id,))


def chunks_for(run_id: str) -> list[dict]:
    return query("SELECT * FROM chunks WHERE run_id = ?", (run_id,))


def claims_for(run_id: str) -> list[dict]:
    rows = query("SELECT * FROM claims WHERE run_id = ?", (run_id,))
    for r in rows:
        r["numbers"] = json.loads(r.pop("numbers_json") or "[]")
    return rows


def edges_for(run_id: str) -> list[dict]:
    return query("SELECT src, dst, type, note FROM edges WHERE run_id = ?", (run_id,))


def sentences_for(run_id: str) -> list[dict]:
    rows = query("SELECT * FROM sentences WHERE run_id = ? ORDER BY id", (run_id,))
    for r in rows:
        r["claim_ids"] = json.loads(r["claim_ids"] or "[]")
        r["checks"] = json.loads(r["checks_json"] or "[]")
        r["hedged"] = bool(r["hedged"])
        r["derived"] = bool(r["derived"])
    return rows


def add_correction(run_id: str, text: str, created_at: str) -> None:
    _write(
        "INSERT INTO corrections (run_id, text, created_at) VALUES (?, ?, ?)",
        (run_id, text, created_at),
    )


def corrections_for(run_id: str) -> list[dict]:
    return query("SELECT id, text, created_at FROM corrections WHERE run_id = ? ORDER BY id", (run_id,))
