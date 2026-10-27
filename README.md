# Glassbox

Glassbox is a desk for one question a brokerage research team actually argues about: did Schwab’s third-quarter 2026 cash movement mean clients were sorting cash out for yield, or did they put cash back into markets?

The hosted app opens on that question already answered. The report, the evidence graph, and the agent log are the saved result of this prompt:

> Did Schwab's third-quarter cash movement mark a return of cash sorting, or did clients reinvest cash in markets?

No API key is required to read that result.

## What the models do

A new report, when Groq and NVIDIA keys are present, does not ask one model to write a paragraph and stop.

- gpt-oss-20b on Groq reads each public filing or call and returns claims as JSON, with a quote copied from the page. It also labels a few cross-company pairs that keyword search cannot decide.
- gpt-oss-120b on Groq drafts the report. Every sentence has to name the claim ids it used.
- A Python checker then refuses a sentence whose number is not in the source, whose source is dated after the as-of date, whose quote is not in the document, or which attributes a peer’s figure to Schwab.
- NVIDIA NIM answers a separate yes-or-no question: does the quote actually entail the sentence? Failures go back to the writer. A sentence that still fails stays on the page, marked unsupported, instead of being deleted.

The four demo reports in a local run are written from the cached filings so the checks can be shown with the keys off. The hosted build shows the Schwab report from that checked draft. Paywalled pages are logged and skipped. `robots.txt` is honored.

## The numbers

Schwab’s own October 15, 2026 release says transactional sweep cash ended September at $492.8 billion, up $7.1 billion. The June 30 release says $485.7 billion. Short credits, which sit inside that definition, were $43.7 billion in June and $63.3 billion in September. Subtracting those published figures from the published totals gives $442.0 billion and $429.5 billion, a decline of $12.5 billion. That is the third-party reading, recomputed from Schwab’s lines, not a number Schwab reported as its sweep change.

The migration scenario uses the latest sweep balance knowable on the as-of date, a labeled 250 basis point spread, and migration of 2%, 5%, and 10%. Schwab’s 3.04% firm-wide net interest margin is shown beside the scenario and is not used as the spread. An April 17, 2026 cut of the same desk only uses the October 16, 2025 release, because the later figures were not public yet.

## Who it is for

The user is an analyst or a risk manager inside a broker who has to explain a cash-sweep move before the next open. The first step is the report already on screen: the finding, the sentence it came from, the filing link, and the check that failed. A correction reruns only the writer and the verifier.

## What is different

Most research copilots hide the source once the paragraph sounds finished. Glassbox keeps the filing, the claim, and the sentence on one graph. A peer’s 2.2% cash ratio cannot be narrated as Schwab’s. A contradiction between the reported increase and the ex-short decline is drawn and left unresolved.

## Run it locally

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000

cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Copy `.env.example` to `.env` for live model calls. The evaluation script is `backend/evaluate.py`. It scores extraction against hand-labeled claims and runs 12 planted false sentences through the same code checks.
