"""On-disk response cache keyed by provider, model, and prompt."""

import hashlib
import json
from typing import Any

from .config import CACHE_DIR


def _key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def get(payload: dict) -> dict | None:
    path = CACHE_DIR / f"{_key(payload)}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def put(payload: dict, response: dict) -> None:
    path = CACHE_DIR / f"{_key(payload)}.json"
    path.write_text(json.dumps({"request": payload, "response": response}, ensure_ascii=False))


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]
