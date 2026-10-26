"""Live fetch path. The demo runs from the cache. One URL can be fetched if you ask for it.

Paywalled hosts are logged and skipped. robots.txt is checked. Nothing here tries to get around either.
"""

from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from .config import settings

PAYWALL_HOSTS = ("wsj.com", "ft.com", "bloomberg.com", "nytimes.com", "barrons.com")


def _paywalled(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return any(host == item or host.endswith("." + item) for item in PAYWALL_HOSTS)


async def robots_allowed(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
            res = await client.get(robots_url, headers={"User-Agent": settings.edgar_ua})
        if res.status_code >= 400:
            return False
    except Exception:
        return False
    parser = RobotFileParser()
    parser.parse(res.text.splitlines())
    return parser.can_fetch(settings.edgar_ua, url)


async def fetch_url(url: str) -> dict:
    if _paywalled(url):
        return {"url": url, "status": "unavailable", "reason": "paywall", "text": ""}
    allowed = await robots_allowed(url)
    if not allowed:
        return {"url": url, "status": "unavailable", "reason": "robots", "text": ""}
    headers = {"User-Agent": settings.edgar_ua, "Accept": "text/html,application/pdf"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        res = await client.get(url, headers=headers)
    if res.status_code >= 400:
        return {"url": url, "status": "unavailable", "reason": f"http {res.status_code}", "text": ""}
    body = res.text
    text = body
    if "pdf" in (res.headers.get("content-type") or "") or url.lower().endswith(".pdf"):
        try:
            import io
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(res.content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages[:8])
        except Exception:
            text = ""
    else:
        try:
            import trafilatura
            extracted = trafilatura.extract(body) or ""
            if extracted:
                text = extracted
        except Exception:
            text = body
    return {"url": url, "status": "fetched", "reason": "", "text": text[:20000]}
