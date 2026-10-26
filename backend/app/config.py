"""Settings. Model ids are the ones this demo was sized for. Confirm them in each console."""

from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

DATA = ROOT / "backend" / "data"
DB_PATH = DATA / "glassbox.db"
CACHE_DIR = DATA / "cache"

# 10 documents per collection job (Schwab, peers, news), not 10 total.
MAX_DOCS_PER_JOB = 10


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


class Settings:
    groq_api_key = _get("GROQ_API_KEY")
    nvidia_api_key = _get("NVIDIA_API_KEY")
    groq_base = _get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    nim_base = _get("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
    groq_fast = _get("GROQ_FAST_MODEL", "openai/gpt-oss-20b")
    groq_writer = _get("GROQ_WRITER_MODEL", "openai/gpt-oss-120b")
    nim_verifier = _get("NIM_VERIFIER_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1.5")
    groq_rpm = int(_get("GROQ_RPM", "30") or "30")
    nim_rpm = int(_get("NIM_RPM", "20") or "20")
    edgar_ua = _get("EDGAR_USER_AGENT", "GlassboxHackathon/1.0 (research demo; contact@localhost)")


settings = Settings()
DATA.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
