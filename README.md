# Glassbox

Evidence desk for one question: did Schwab’s third-quarter cash move mean cash sorting was back, or did clients put cash to work?

The orchestrator is plain async code. Its task graph is fixed: collect, chunk, extract, link, write, verify. Say that in the demo.

## Document cap

“Max 10 sources per scrape” is implemented as **10 documents per collection job**. There are three jobs: Schwab, peers, and news. That is about 30 documents at most, not 10 in total. The cached corpus is under that cap. LPL’s third-quarter release is dated October 27, 2026, so it is not in the cache. A `wsj.com` discovery hit is logged as paywalled and is not fetched.

## Run

```bash
# from the repo root, keys live in .env
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000

# second terminal
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

Leave the keys blank and the four seeded reports still run from the cached filings. Paste `GROQ_API_KEY` and `NVIDIA_API_KEY` into `.env` and restart the API when a new report should call the models. Confirm the model ids and the RPM placeholders in the Groq and NVIDIA consoles before a live run. The migration scenario is a section of the report, not a separate page.

- Collector tag and extractor: `openai/gpt-oss-20b` on Groq
- Linker: BM25 in code. The fast Groq model is only for a borderline document, not for every pair.
- Writer: `openai/gpt-oss-120b` on Groq
- Verifier entailment: `nvidia/llama-3.3-nemotron-super-49b-v1.5` on NVIDIA NIM
- Failover swaps the two providers on a 429 or a 5xx

## Evaluation

```bash
cd backend && .venv/bin/python evaluate.py
```

The script writes `backend/data/evaluation.json`. It scores extraction against the hand-labeled claims, runs 12 seeded false sentences through the code checks, and compares that with a one-prompt baseline that does not run those checks. One seeded sentence passes the code checks and needs the NIM entailment pass. Without a key, that miss is reported rather than marked caught.

## Finance

The scenario uses the latest Schwab sweep balance published on or before the as-of date, a labeled 250 basis point spread, and migration of 2%, 5%, and 10%. The 3.04% net interest margin is shown and is not used as the spread. The $12.5 billion third-party decline is recomputed as June sweep minus June short credits, minus the same cut for September: 442.0 − 429.5 = 12.5.
