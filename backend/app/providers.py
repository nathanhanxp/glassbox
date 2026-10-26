"""Groq and NVIDIA NIM. Each call is cached. A 429 or 5xx fails over to the other provider."""

import time
from typing import Any

import httpx

from . import cache
from .config import settings
from .ratelimit import RateLimiter

_groq_limit = RateLimiter(settings.groq_rpm)
_nim_limit = RateLimiter(settings.nim_rpm)

USAGE = {"calls": 0, "tokens": 0, "failover": 0}


def reset_usage() -> None:
    USAGE["calls"] = 0
    USAGE["tokens"] = 0
    USAGE["failover"] = 0


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


async def _post(base: str, api_key: str, payload: dict, limiter: RateLimiter) -> dict:
    await limiter.wait()
    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(
            f"{base.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
        )
    if res.status_code >= 400:
        raise RuntimeError(f"{res.status_code} {res.text[:300]}")
    return res.json()


def _text_of(data: dict) -> str:
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return ""


async def complete(
    *,
    purpose: str,
    system: str,
    user: str,
    preferred: str,
    max_tokens: int = 700,
    temperature: float = 0.1,
) -> dict[str, Any]:
    """preferred is 'groq-fast', 'groq-writer', or 'nim'."""
    routes = {
        "groq-fast": ("groq", settings.groq_fast, settings.groq_api_key, settings.groq_base, _groq_limit),
        "groq-writer": ("groq", settings.groq_writer, settings.groq_api_key, settings.groq_base, _groq_limit),
        "nim": ("nim", settings.nim_verifier, settings.nvidia_api_key, settings.nim_base, _nim_limit),
    }
    primary = routes[preferred]
    failover = routes["nim"] if preferred.startswith("groq") else routes["groq-writer"]
    order = [primary]
    if failover[2]:
        order.append(failover)

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    last_error = "no provider key"
    for index, (provider, model, key, base, limiter) in enumerate(order):
        if not key:
            last_error = f"{provider} key missing"
            continue
        payload = {
            "provider": provider,
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "purpose": purpose,
        }
        cached = cache.get(payload)
        if cached:
            text = _text_of(cached["response"])
            return {"text": text, "provider": provider, "model": model, "cached": True, "tokens": _estimate_tokens(system + user + text)}
        started = time.perf_counter()
        try:
            data = await _post(base, key, {k: payload[k] for k in ("model", "messages", "temperature", "max_tokens")}, limiter)
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            if index < len(order) - 1:
                USAGE["failover"] += 1
            continue
        cache.put(payload, data)
        text = _text_of(data)
        tokens = _estimate_tokens(system + user + text)
        usage = data.get("usage") or {}
        if usage.get("total_tokens"):
            tokens = int(usage["total_tokens"])
        USAGE["calls"] += 1
        USAGE["tokens"] += tokens
        return {
            "text": text,
            "provider": provider,
            "model": model,
            "cached": False,
            "tokens": tokens,
            "latency_ms": int((time.perf_counter() - started) * 1000),
        }
    return {"text": "", "provider": None, "model": None, "cached": False, "tokens": 0, "error": last_error}
