"""Scenario math. Every input is sourced. The yield spread is an assumption, labeled as one."""

SPREAD = 0.025  # 250 basis points. Assumption, not a figure from a filing.
SPREAD_LABEL = "250 basis point net yield spread on sweep cash that leaves the balance sheet"


def _money(billions: float, rate: float) -> float:
    return round(billions * 1_000_000_000 * rate * SPREAD, 0)


def scenario(as_of: str) -> dict:
    """Use the latest sweep balance whose publication date is on or before as_of."""
    knowable = []
    if as_of >= "2025-10-16":
        knowable.append(
            {
                "balance_billion": 425.6,
                "label": "September 2025 transactional sweep cash",
                "source_id": "schw-q3-2025-release",
                "source": "Schwab Q3 2025 release, October 16, 2025",
                "published_at": "2025-10-16",
            }
        )
    if as_of >= "2026-09-15":
        knowable.append(
            {
                "balance_billion": 483.3,
                "label": "August 2026 transactional sweep cash",
                "source_id": "schw-aug-2026-monthly",
                "source": "Schwab monthly activity report, September 15, 2026",
                "published_at": "2026-09-15",
            }
        )
    if as_of >= "2026-10-15":
        knowable.append(
            {
                "balance_billion": 492.8,
                "label": "September 2026 transactional sweep cash",
                "source_id": "schw-q3-2026-release",
                "source": "Monthly activity table in the Schwab Q3 2026 release, October 15, 2026",
                "published_at": "2026-10-15",
            }
        )
    if not knowable:
        return {
            "knowable": False,
            "reason": "No Schwab sweep balance in the cache was published on or before this as-of date.",
        }

    balance = knowable[-1]
    rows = []
    for pct in (0.02, 0.05, 0.10):
        rows.append(
            {
                "migration": pct,
                "migrated_billion": round(balance["balance_billion"] * pct, 2),
                "annual_revenue_at_risk": _money(balance["balance_billion"], pct),
            }
        )

    recompute = None
    if as_of >= "2026-10-15":
        june_ex = round(485.7 - 43.7, 1)
        sept_ex = round(492.8 - 63.3, 1)
        recompute = {
            "june_sweep_billion": 485.7,
            "june_sweep_source": "Schwab Q2 2026 release, July 21, 2026",
            "june_short_credits_billion": 43.7,
            "june_short_source": "Schwab Q2 2026 release, short cash credits as of June 30, 2026",
            "sept_sweep_billion": 492.8,
            "sept_sweep_source": "Schwab Q3 2026 release, October 15, 2026",
            "sept_short_credits_billion": 63.3,
            "sept_short_source": "Schwab Q3 2026 release footnote, September 2026 short credits",
            "june_ex_short_billion": june_ex,
            "sept_ex_short_billion": sept_ex,
            "decline_billion": round(june_ex - sept_ex, 1),
            "note": (
                "Third parties published a $12.5 billion third-quarter decline. "
                "Subtracting Schwab's own short-credit figures from Schwab's own sweep totals "
                "reproduces that $12.5 billion. It is not the reported change in transactional sweep cash, "
                "which was an increase of $7.1 billion."
            ),
        }

    return {
        "knowable": True,
        "balance": balance,
        "also_knowable": knowable,
        "spread": SPREAD,
        "spread_label": SPREAD_LABEL,
        "spread_note": (
            "Assumption. Schwab's reported net interest margin of 3.04% is a firm-wide margin, "
            "so it is not used as the spread on a migrated sweep dollar."
            if as_of >= "2026-10-15"
            else "Assumption. The 250 basis point spread is labeled as an assumption. Firm-wide net interest margin is not used, and the later reported NIM is not knowable at this as-of date."
        ),
        "formula": "annual revenue at risk = sweep balance × migration share × 250 basis points",
        "rows": rows,
        "recompute": recompute,
        "nim_context": (
            {
                "value": "3.04%",
                "source": "Schwab Q3 2026 release",
                "used_in_scenario": False,
            }
            if as_of >= "2026-10-15"
            else None
        ),
    }
