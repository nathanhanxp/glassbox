"""Six run endpoints, plus a list so the sidebar can load saved reports."""

import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from . import db
from .corpus import DOCUMENTS
from .finance import scenario
from .graph import build_graph
from .pipeline import SCRAPE_DIR, emit, execute, new_run_id, seed_demo, subscribe, unsubscribe

db.init()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await seed_demo()
    yield


app = FastAPI(title="Glassbox", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    question: str = Field(min_length=8)
    as_of: str = "2026-10-26"
    title: str | None = None


class CorrectionRequest(BaseModel):
    text: str = Field(min_length=3)


def _report(run_id: str) -> dict:
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    payload = json.loads(run["report_json"] or "{}")
    payload["created_at"] = run["created_at"]
    payload["corrections"] = db.corrections_for(run_id)
    payload["finance"] = scenario(run["as_of"])
    return payload


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "orchestrator": "async code, fixed task graph"}


@app.get("/api/runs")
def runs() -> list[dict]:
    rows = []
    for run in db.list_runs():
        metrics = json.loads(run["metrics_json"] or "{}")
        rows.append(
            {
                "id": run["id"],
                "title": run["title"],
                "question": run["question"],
                "as_of": run["as_of"],
                "status": run["status"],
                "created_at": run["created_at"],
                "unsupported": metrics.get("unsupported", 0),
            }
        )
    return rows


@app.post("/api/runs")
async def start_run(body: RunRequest) -> dict:
    run_id = new_run_id()
    title = body.title or body.question[:72]
    created = db_now()
    db.insert_run(
        {
            "id": run_id,
            "title": title,
            "question": body.question,
            "as_of": body.as_of,
            "status": "running",
            "created_at": created,
            "report_json": "{}",
            "metrics_json": "{}",
            "gaps_json": "[]",
        }
    )
    asyncio.create_task(
        execute(run_id, title=title, question=body.question, as_of=body.as_of, created_at=created, use_models=True)
    )
    return {"id": run_id, "status": "running"}


@app.get("/api/runs/{run_id}/events")
async def stream_events(run_id: str, replay: int = 0):
    if not db.get_run(run_id):
        raise HTTPException(404, "Run not found")

    async def generate():
        seen = [event["id"] for event in db.events_for(run_id)]
        queue = subscribe(run_id)
        try:
            for event in db.events_for(run_id):
                if event["id"] not in seen:
                    seen.append(event["id"])
                if replay:
                    await asyncio.sleep(0.12)
                yield f"data: {json.dumps(event)}\n\n"
            if replay:
                yield f"data: {json.dumps({'kind': 'done', 'agent': 'Orchestrator', 'message': 'Replay finished.'})}\n\n"
                return
            while True:
                item = await queue.get()
                if item is not None and item.get("id") in seen:
                    continue
                if item is not None and item.get("id") is not None:
                    seen.append(item["id"])
                if item is None:
                    yield f"data: {json.dumps({'kind': 'done', 'agent': 'Orchestrator', 'message': 'Run finished.'})}\n\n"
                    break
                yield f"data: {json.dumps(item)}\n\n"
        finally:
            unsubscribe(run_id, queue)

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/runs/{run_id}/sources")
def sources(run_id: str) -> list[dict]:
    if not db.get_run(run_id):
        raise HTTPException(404, "Run not found")
    manifest = SCRAPE_DIR / run_id / "checked.json"
    if manifest.exists():
        return json.loads(manifest.read_text(encoding="utf-8"))
    stored = {d["id"]: d for d in db.docs_for(run_id)}
    rows = []
    for doc in DOCUMENTS:
        saved = stored.get(doc["id"])
        rows.append(
            {
                "id": doc["id"],
                "job": doc["job"],
                "title": doc["title"],
                "url": doc.get("url"),
                "published_at": doc.get("published_at"),
                "company": doc.get("company"),
                "decision": "keep" if saved else "drop",
                "status": (saved or {}).get("status") or "not stored",
            }
        )
    return rows


@app.get("/api/runs/{run_id}/graph")
def graph(run_id: str, as_of: str | None = None) -> dict:
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return build_graph(
        db.docs_for(run_id),
        db.claims_for(run_id),
        db.edges_for(run_id),
        db.sentences_for(run_id),
        as_of or run["as_of"],
    )


@app.get("/api/runs/{run_id}/report")
def report(run_id: str) -> dict:
    return _report(run_id)


@app.post("/api/runs/{run_id}/corrections")
async def correct(run_id: str, body: CorrectionRequest) -> dict:
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    created = db_now()
    db.add_correction(run_id, body.text, created)
    claim = {
        "id": f"user-{created.replace(':', '').replace('-', '')}",
        "text": body.text.strip(),
        "quote": "",
        "chunk_id": "",
        "doc_id": "",
        "company": "USER",
        "tier": "user",
        "published_at": run["as_of"],
        "scope": "user_assertion",
        "event_type": "user",
        "numbers": [],
        "short_label": "Your note",
    }
    db.add_claim(run_id, claim)
    await execute(
        run_id,
        title=run["title"],
        question=run["question"],
        as_of=run["as_of"],
        created_at=run["created_at"],
        rewrite_only=True,
        user_note=body.text.strip(),
    )
    return _report(run_id)


@app.post("/api/runs/{run_id}/replay")
async def replay(run_id: str) -> dict:
    if not db.get_run(run_id):
        raise HTTPException(404, "Run not found")
    await emit(run_id, "Orchestrator", "replay", "Replaying the saved event log. No models are called.", {})
    return {"id": run_id, "replay": True}


def db_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
