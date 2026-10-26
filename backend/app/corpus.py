"""Cached corpus. Dates and tiers are set here in code, from page metadata and filing dates, never by a model.

Cleaned text is short passages copied from public filings, releases, the earnings-call transcript,
and two secondary writeups. Quotes in the report have to appear in this text.
"""

COMPANIES = {
    "SCHW": "Charles Schwab",
    "LPLA": "LPL Financial",
    "RJF": "Raymond James",
    "AMP": "Ameriprise",
    "MS": "Morgan Stanley",
    "JPM": "JPMorgan",
}

Q3_SWEEP = (
    "Client transactional sweep cash balances ended September at $492.8 billion, an increase of $7.1 billion "
    "versus the prior quarter-end, reflecting continued demand for long/short strategies and organic growth, "
    "partially offset by client asset allocation decisions."
)
Q3_NIM = "Net interest margin expanded quarter-over-quarter to 3.04%."
Q3_REV = "Quarterly net revenues grew year-over-year by 17% to a record $7.2 billion."
Q3_SHORT = (
    "For the month of September 2026, margin loans totaled $60.7 billion and short credits totaled $63.3 billion."
)
Q3_SWEEP_DEF = (
    "Transactional sweep cash includes bank sweep deposits, broker-dealer cash balances, other client cash held "
    "on the balance sheet (such as bank checking and savings deposits, short credits related to certain client "
    "long/short strategies, and broker-dealer non-interest-bearing credits), and bank deposit account balances; "
    "excludes proprietary and third-party CDs."
)
Q3_TABLE = (
    "Transactional Sweep Cash (at month end) 425.6 428.8 427.5 453.7 433.3 436.1 461.5 467.6 472.4 485.7 476.8 483.3 492.8"
)
Q3_CHARLEY = (
    "Introduced Charley, a new AI-powered assistant that provides U.S. retail clients with conversational access "
    "to Schwab's tools and insights."
)
Q3_NNA = "Core net new assets totaled $190.4 billion, up 38% versus 3Q25."
Q3_MM = "Schwab money market funds $699,067"

CALL_SWEEP = (
    "Transactional sweep cash balances finished the quarter at $492.8 billion, up $7.1 billion quarter-over-quarter, "
    "reflecting an increase in the long/short strategy and organic growth, partially offset by clients reinvesting "
    "in markets given improving sentiment."
)
CALL_MARKET = (
    "What we saw in the third quarter with client sentiment improving more consistently through the third quarter, "
    "we saw cash go back into the market. Part of that was fueled by the activity in IPOs as well."
)
CALL_NOT_SORTING = (
    "In terms of cash, just to be clear, even with those higher rates, this is not cash sorting in any way."
)
CALL_CHARLIE = (
    "We just introduced Charlie, our new AI-powered conversational assistant, that will be available to all clients "
    "in the coming months."
)
CALL_AI_SHARE = (
    "77% of U.S. investors use AI today, and at the same time, more than 90% prefer human involvement alongside AI technology."
)
CALL_BLOCK = "First, we are blocking unauthorized agents who try to log in on behalf of clients."
CALL_TRADERS = (
    "A subset of traders are already using AI to support their trading goals, connecting their LLMs to Schwab via "
    "our APIs and our MCP server. As an interesting aside, this group actually holds more cash than other active "
    "traders because they are focused on finding their next great investment."
)
CALL_DOUBLED = (
    "It has doubled in about the last six months. As I shared earlier, that higher level of engagement actually "
    "leads to more cash held by those clients. I know one of the fears in the market about us is that as AI takes "
    "off, it will impact cash levels. We are actually seeing the opposite impact, that the more people use AI, "
    "the more cash they hold because they are more active in buying stocks."
)
CALL_25 = "Our technologists are 25% more productive this year than they were last year."
CALL_190 = "We still have $190 billion roughly of securities that are yielding sub 2%."
CALL_PEOPLE = (
    "That combination of people and technology has always been central to Schwab and cannot be underestimated."
)

Q2_SWEEP = (
    "Client transactional sweep cash balances ended June at $485.7 billion, an increase of $24.2 billion versus "
    "the prior quarter-end, reflecting typical 2Q tax seasonality, organic growth, and client asset allocation decisions."
)
Q2_SHORT = (
    "Long/short strategy interest remained strong amongst RIA clients, with margin loan debits and short cash "
    "credits equaling $42.1 billion and $43.7 billion, respectively, as of June 30, 2026."
)
Q2_AI = (
    "Introduced Portfolio Insights, a generative AI-powered capability that helps investors understand portfolio performance."
)
Q2_REV = "During the second quarter, strong client engagement helped drive year-over-year revenue growth of 21% to a record $7.1 billion."

TENQ_CASH = (
    "Client cash activity during the second quarter and first six months of 2026 reflected seasonality, organic "
    "growth from asset gathering, and client asset allocation decisions. Bank sweep deposits and payables to "
    "brokerage clients increased by a total of $42.7 billion, or 14%, from June 30, 2025 to the end of the second "
    "quarter of 2026 and $3.6 billion, or 1%, from December 31, 2025."
)

AUG_SWEEP = (
    "Transactional sweep cash increased $6.5 billion to end August at $483.3 billion, driven by continued client "
    "demand for long/short strategies."
)

Y2025_SWEEP = (
    "Client transactional sweep cash balances ended September at $425.6 billion, an increase of $13.5 billion "
    "versus the prior quarter-end, reflecting organic growth, client net buying activity, and seasonality."
)
Y2025_FUND = "Bank Supplemental Funding declined by $12.9 billion to end the quarter at $14.8 billion."
Y2025_QUOTE = (
    "Client transactional sweep cash grew by $13.5 billion versus 2Q25, helping us to further reduce higher cost "
    "bank funding by $12.9 billion to $14.8 billion at quarter-end."
)

LPL_CASH = (
    "Total client cash balances were $57 billion, a decrease of $2 billion sequentially and an increase of $6 billion year-over-year."
)
LPL_RATIO = (
    "Client cash balances as a percentage of total client assets were 2.2%, down from 2.5% in the prior quarter and 2.6% in the prior year."
)
LPL_ASSETS = "Total client assets increased 34% year-over-year to $2.6 trillion."

RJF_SWEEP = (
    "Clients' domestic cash sweep and enhanced savings program balances ended the quarter at $58.8 billion, up 2% "
    "from the preceding quarter and 7% over the prior year level representing 3.4% of domestic PCG client assets at quarter end."
)
RJF_AI = (
    "This quarter, we completed the enterprise rollout of Raymond, our proprietary AI assistant following a thoughtful pilot program and phase deployment."
)

AMP_Q2 = "Cash sweep balances were $28.8 billion compared to $29.4 billion in the prior quarter, reflecting normal seasonal patterns."
AMP_Q1 = "Cash sweep balances were stable at $29.4 billion compared to $29.9 billion in the prior quarter, reflecting normal seasonal patterns."
AMP_AI = (
    "Our ongoing investments are reinforcing our leadership in advice, wealth management solutions and our technology "
    "ecosystem, including our AI capabilities."
)

MS_Q3 = (
    "Wealth Management delivered record net revenues of $9.1 billion on robust asset management fees and higher net "
    "interest income, generating a pre-tax margin of 30.4%."
)
MS_Q3_SWEEP = (
    "Net interest income increased from a year ago primarily driven by the cumulative impact of lending growth and higher average sweep deposits."
)
MS_Q2_SWEEP = (
    "Net interest income increased from a year ago primarily driven by higher average sweep deposits and the cumulative impact of lending growth."
)

JPM_Q3_DEP = "Average deposits up 4% YoY, flat QoQ; client investment assets up 15% YoY."
JPM_Q2_WEALTH = "In wealth management, first-time investors of nearly 44,000 set a new record."
JPM_Q2_DEP = "Average deposits up 3% YoY, up 2% QoQ; client investment assets up 21% YoY."

AARDVARK = (
    "The cash-sweep debate is back, this time framed around AI agents. September's agent-driven sell-off in brokers "
    "put idle cash back at the center of the stock, and stripping long/short short credits out of transactional "
    "sweep cash shows a ($12.5B) sequential decline beneath the reported +$7.1B. Management blocks unauthorized "
    "agents and says AI-connected traders hold more cash, not less."
)
AARDVARK_TABLE = "Sweep cash ex long/short $442.0B in June and $429.5B in September, a decline of ($12.5B)."

TRADEFLOCK = (
    "The release says client transactional sweep cash ended September at $492.8 billion, up $7.1 billion from June. "
    "By TradeFlock's estimate, sweep cash outside short credits fell about $12.5 billion, or 2.8%, in the quarter. "
    "Schwab's own wording says the increase reflected continued demand for long/short strategies and organic growth, "
    "partially offset by client asset allocation decisions. Asked whether higher rates were driving clients out of "
    "cash, Verdeschi said this is not cash sorting in any way."
)


def _doc(**kwargs) -> dict:
    kwargs.setdefault("status", "cached")
    kwargs.setdefault("date_origin", "page_or_filing_date")
    kwargs.setdefault("text", "")
    return kwargs


DOCUMENTS: list[dict] = [
    _doc(
        id="schw-q3-2026-release",
        job="schwab",
        company="SCHW",
        title="Schwab Q3 2026 earnings release, Exhibit 99.1",
        short_label="Q3 release · Oct",
        url="https://www.sec.gov/Archives/edgar/data/316709/000031670926000035/a3q26exhibit991.htm",
        published_at="2026-10-15",
        tier="primary",
        source_kind="filing",
        text="\n".join([
            "WESTLAKE, Texas, October 15, 2026. The Charles Schwab Corporation reported third quarter results.",
            Q3_SWEEP,
            Q3_NIM,
            Q3_REV,
            Q3_NNA,
            Q3_CHARLEY,
            Q3_SHORT,
            Q3_SWEEP_DEF,
            Q3_TABLE + ".",
            Q3_MM + ".",
            "These forward-looking statements reflect management's expectations as of the date hereof.",
        ]),
    ),
    _doc(
        id="schw-q3-2026-call",
        job="schwab",
        company="SCHW",
        title="Schwab Q3 2026 earnings call (transcript host: Motley Fool)",
        short_label="Q3 call · Oct",
        url="https://www.fool.com/earnings/call-transcripts/2026/10/15/schwab-schw-q3-2026-earnings-call-transcript/",
        published_at="2026-10-15",
        tier="primary",
        source_kind="company_call",
        date_origin="call_date_on_transcript_page",
        text="\n".join([
            "Rick Wurster, President and CEO, and Mike Verdeschi, CFO, October 15, 2026.",
            CALL_CHARLIE,
            CALL_AI_SHARE,
            CALL_PEOPLE,
            CALL_BLOCK,
            CALL_TRADERS,
            CALL_DOUBLED,
            CALL_25,
            CALL_SWEEP,
            CALL_MARKET,
            CALL_190,
            CALL_NOT_SORTING,
        ]),
    ),
    _doc(
        id="schw-aug-2026-monthly",
        job="schwab",
        company="SCHW",
        title="Schwab monthly activity highlights, August 2026",
        short_label="Monthly · Aug",
        url="https://pressroom.aboutschwab.com/press-releases/press-release/2026/Schwab-Reports-Monthly-Activity-Highlights-7c5bb81a9/default.aspx",
        published_at="2026-09-15",
        tier="primary",
        source_kind="press",
        text="\n".join([
            "Schwab Reports Monthly Activity Highlights. 09/15/2026.",
            AUG_SWEEP,
            "Total client assets equaled $13.41 trillion as of month-end August.",
        ]),
    ),
    _doc(
        id="schw-10q-2026-q2",
        job="schwab",
        company="SCHW",
        title="Schwab Form 10-Q for the quarter ended June 30, 2026",
        short_label="10-Q · Aug 7",
        url="https://www.sec.gov/Archives/edgar/data/316709/000031670926000031/schw-20260630.htm",
        published_at="2026-08-07",
        tier="primary",
        source_kind="filing",
        text=TENQ_CASH,
    ),
    _doc(
        id="schw-q2-2026-release",
        job="schwab",
        company="SCHW",
        title="Schwab Q2 2026 earnings release, Exhibit 99.1",
        short_label="Q2 release · Jul",
        url="https://www.sec.gov/Archives/edgar/data/316709/000031670926000027/a2q26exhibit991.htm",
        published_at="2026-07-21",
        tier="primary",
        source_kind="filing",
        text="\n".join([
            "WESTLAKE, Texas, July 21, 2026. The Charles Schwab Corporation reported second quarter results.",
            Q2_SWEEP,
            Q2_SHORT,
            Q2_REV,
            Q2_AI,
        ]),
    ),
    _doc(
        id="schw-q3-2025-release",
        job="schwab",
        company="SCHW",
        title="Schwab Q3 2025 earnings release",
        short_label="Q3 release · 2025",
        url="https://pressroom.aboutschwab.com/press-releases/press-release/2025/Schwab-Reports-Record-Revenue-and-Earnings/default.aspx",
        published_at="2025-10-16",
        tier="primary",
        source_kind="press",
        text="\n".join([
            "10/16/2025. The Charles Schwab Corporation reported third quarter 2025 results.",
            Y2025_SWEEP,
            Y2025_FUND,
            Y2025_QUOTE,
        ]),
    ),
    _doc(
        id="lpl-q2-2026",
        job="peers",
        company="LPLA",
        title="LPL Financial second quarter 2026 results",
        short_label="LPL Q2 · Jul",
        url="https://investor.lpl.com/news-releases/news-release-details/lpl-financial-announces-second-quarter-2026-results",
        published_at="2026-07-30",
        tier="primary",
        source_kind="press",
        text="\n".join([
            "LPL Financial Announces Second Quarter 2026 Results. Jul 30, 2026.",
            LPL_ASSETS,
            LPL_CASH,
            LPL_RATIO,
        ]),
    ),
    _doc(
        id="rjf-q3-2026-call",
        job="peers",
        company="RJF",
        title="Raymond James fiscal Q3 2026 earnings call",
        short_label="RJF call · Jul",
        url="https://www.sec.gov/Archives/edgar/data/720005/000072000526000066/rjf-20260722.htm",
        published_at="2026-07-22",
        tier="secondary",
        source_kind="transcript",
        date_origin="earnings_8k_filing_date",
        text="\n".join([
            "Raymond James fiscal third quarter 2026 earnings call. Earnings 8-K filed July 22, 2026. Transcript host: TickerTrends.",
            RJF_SWEEP,
            RJF_AI,
        ]),
    ),
    _doc(
        id="amp-q2-2026",
        job="peers",
        company="AMP",
        title="Ameriprise Q2 2026 earnings release",
        short_label="AMP Q2 · Jul",
        url="https://www.sec.gov/Archives/edgar/data/820027/000082002726000038/q22026er.htm",
        published_at="2026-07-23",
        tier="primary",
        source_kind="filing",
        text="\n".join([
            "Ameriprise Financial earnings release furnished July 23, 2026.",
            AMP_Q2,
            AMP_AI,
        ]),
    ),
    _doc(
        id="amp-q1-2026",
        job="peers",
        company="AMP",
        title="Ameriprise Q1 2026 earnings release",
        short_label="AMP Q1 · Apr",
        url="https://www.sec.gov/Archives/edgar/data/820027/000082002726000020/q12026er.htm",
        published_at="2026-04-23",
        tier="primary",
        source_kind="filing",
        text="\n".join([
            "Ameriprise Financial earnings release furnished April 23, 2026.",
            AMP_Q1,
        ]),
    ),
    _doc(
        id="ms-q3-2026",
        job="peers",
        company="MS",
        title="Morgan Stanley Q3 2026 earnings release",
        short_label="MS Q3 · Oct",
        url="https://www.sec.gov/Archives/edgar/data/895421/000089542126000288/a3q26msearningsrelease.htm",
        published_at="2026-10-14",
        tier="primary",
        source_kind="filing",
        text="\n".join([
            "Morgan Stanley earnings release furnished October 14, 2026.",
            MS_Q3,
            MS_Q3_SWEEP,
        ]),
    ),
    _doc(
        id="ms-q2-2026",
        job="peers",
        company="MS",
        title="Morgan Stanley Q2 2026 earnings release",
        short_label="MS Q2 · Jul",
        url="https://www.sec.gov/Archives/edgar/data/895421/000089542126000207/a2q26msearningsrelease.htm",
        published_at="2026-07-15",
        tier="primary",
        source_kind="filing",
        text="\n".join([
            "Morgan Stanley earnings release furnished July 15, 2026.",
            MS_Q2_SWEEP,
        ]),
    ),
    _doc(
        id="jpm-q3-2026",
        job="peers",
        company="JPM",
        title="JPMorgan Q3 2026 earnings release",
        short_label="JPM Q3 · Oct",
        url="https://www.sec.gov/Archives/edgar/data/19617/000162828026065582/a3q26erfexhibit991narrative.htm",
        published_at="2026-10-13",
        tier="primary",
        source_kind="filing",
        text="\n".join([
            "JPMorgan Chase earnings release furnished October 13, 2026.",
            JPM_Q3_DEP,
        ]),
    ),
    _doc(
        id="jpm-q2-2026",
        job="peers",
        company="JPM",
        title="JPMorgan Q2 2026 earnings release",
        short_label="JPM Q2 · Jul",
        url="https://www.sec.gov/Archives/edgar/data/19617/000162828026048078/a2q26erfexhibit991narrative.htm",
        published_at="2026-07-14",
        tier="primary",
        source_kind="filing",
        text="\n".join([
            "JPMorgan Chase earnings release furnished July 14, 2026.",
            JPM_Q2_DEP,
            JPM_Q2_WEALTH,
        ]),
    ),
    _doc(
        id="news-aardvark",
        job="news",
        company="SCHW",
        title="Aardvark Labs, Schwab Q3 2026 earnings recap",
        short_label="Aardvark · Oct 21",
        url="https://research.aardvarklabs.co/research/schw/earnings/2026-q3/schw-2026-q3-recap",
        published_at="2026-10-21",
        tier="secondary",
        source_kind="analyst",
        text="\n".join([
            "Published: October 21, 2026. Aardvark Labs.",
            AARDVARK,
            AARDVARK_TABLE,
        ]),
    ),
    _doc(
        id="news-tradeflock",
        job="news",
        company="SCHW",
        title="TradeFlock: sweep cash fell excluding short credits",
        short_label="TradeFlock",
        url="https://www.tradeflock.net/schwab-earnings-sweep-cash-excluding-short-credits",
        published_at="2026-10-16",
        tier="secondary",
        source_kind="news",
        date_origin="no_dateline_in_captured_text_day_after_oct_15_release",
        text=TRADEFLOCK,
    ),
]

BY_ID = {d["id"]: d for d in DOCUMENTS}

# Fixed peer list from the brief. Two slots each. Cached when a public filing was retrieved.
PEER_TARGETS = [
    {"company": "LPLA", "name": "LPL Financial"},
    {"company": "RJF", "name": "Raymond James"},
    {"company": "AMP", "name": "Ameriprise"},
    {"company": "MS", "name": "Morgan Stanley"},
    {"company": "JPM", "name": "JPMorgan"},
]
