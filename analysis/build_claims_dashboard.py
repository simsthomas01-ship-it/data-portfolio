#!/usr/bin/env python3
"""Build output/claims-data.json from the claims practice database.

Runs with plain python3 (sqlite3 is in the standard library). It loads
sql/claims_practice_setup.sql into an in-memory database, runs the
queries below, and writes one small JSON file that the public dashboard page
reads. Nothing is queried when a visitor opens the page.
"""
import json
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETUP = ROOT / "sql" / "claims_practice_setup.sql"
OUT = ROOT / "output" / "claims-data.json"

# One row per claim / per coverage, already joined, so the page can filter
# by province in the browser.
CLAIM_ROWS = """
SELECT strftime('%Y', c.loss_date), p.province, g.group_name, v.make,
       ROUND(c.reported_loss, 2)
FROM claim c
JOIN vehicle v USING (vin)
JOIN policy p USING (policy_number)
JOIN coverage_description d USING (coverage_description_id)
JOIN coverage_group g USING (coverage_group_id)
"""
PREMIUM_ROWS = """
SELECT p.province, g.group_name, ROUND(co.premium, 2)
FROM coverage co
JOIN vehicle v USING (vin)
JOIN policy p USING (policy_number)
JOIN coverage_description d USING (coverage_description_id)
JOIN coverage_group g USING (coverage_group_id)
"""
VEHICLES = """
SELECT p.province, COUNT(*) FROM vehicle v
JOIN policy p USING (policy_number) GROUP BY p.province
"""

# The SQL shown on the page under "How this was built".
SHOWCASE = [
    {
        "title": "Loss ratio by province",
        "question": "Which provinces are paying out more than they collect?",
        "note": "Losses and premiums are summed in separate steps and joined afterwards. Joining claim to coverage first would repeat every premium once per claim and inflate the total.",
        "sql": """WITH loss AS (
  SELECT p.province, SUM(c.reported_loss) AS losses
  FROM claim c
  JOIN vehicle v USING (vin)
  JOIN policy p USING (policy_number)
  GROUP BY p.province
),
prem AS (
  SELECT p.province, SUM(co.premium) AS premium
  FROM coverage co
  JOIN vehicle v USING (vin)
  JOIN policy p USING (policy_number)
  GROUP BY p.province
)
SELECT prem.province,
       ROUND(100.0 * loss.losses / prem.premium, 1) AS loss_ratio_pct
FROM prem
JOIN loss USING (province)
ORDER BY loss_ratio_pct DESC;""",
    },
    {
        "title": "Reported losses by year",
        "question": "How have losses moved over time?",
        "note": "Grouped by the year of the loss date, not the policy year.",
        "sql": """SELECT strftime('%Y', loss_date) AS loss_year,
       COUNT(*) AS claims,
       ROUND(SUM(reported_loss), 2) AS losses
FROM claim
GROUP BY loss_year
ORDER BY loss_year;""",
    },
    {
        "title": "Premium vs. losses by coverage group",
        "question": "Which parts of the product make or lose money?",
        "note": "Same idea as the loss ratio query: aggregate each side separately, then combine.",
        "sql": """WITH prem AS (
  SELECT d.coverage_group_id, SUM(co.premium) AS premium
  FROM coverage co
  JOIN coverage_description d USING (coverage_description_id)
  GROUP BY d.coverage_group_id
),
loss AS (
  SELECT d.coverage_group_id, SUM(c.reported_loss) AS losses
  FROM claim c
  JOIN coverage_description d USING (coverage_description_id)
  GROUP BY d.coverage_group_id
)
SELECT g.group_name, prem.premium, COALESCE(loss.losses, 0) AS losses
FROM coverage_group g
JOIN prem USING (coverage_group_id)
LEFT JOIN loss USING (coverage_group_id)
ORDER BY g.group_name;""",
    },
    {
        "title": "Average claim severity by make",
        "question": "Do some vehicle makes have more expensive claims?",
        "note": "Severity is the average cost per claim, so it says nothing about how often claims happen.",
        "sql": """SELECT v.make,
       COUNT(*) AS claims,
       ROUND(AVG(c.reported_loss), 0) AS avg_severity
FROM claim c
JOIN vehicle v USING (vin)
GROUP BY v.make
ORDER BY avg_severity DESC;""",
    },
]


def main():
    db = sqlite3.connect(":memory:")
    db.executescript(SETUP.read_text())

    claims = [list(r) for r in db.execute(CLAIM_ROWS)]
    prem = [list(r) for r in db.execute(PREMIUM_ROWS)]
    veh = {p: n for p, n in db.execute(VEHICLES)}

    # Every showcase query must run, and the by-year query must agree with the
    # rows the page will use.
    for item in SHOWCASE:
        rows = db.execute(item["sql"]).fetchall()
        assert rows, "empty result: " + item["title"]
    by_year = db.execute(SHOWCASE[1]["sql"]).fetchall()
    assert round(sum(r[2] for r in by_year), 2) == round(sum(r[4] for r in claims), 2)

    payload = {
        "generated": date.today().isoformat(),
        "claims": claims,
        "prem": prem,
        "veh": veh,
        "showcase": SHOWCASE,
    }
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    print("wrote %s (%d bytes): %d claims, %d coverages" % (OUT, OUT.stat().st_size, len(claims), len(prem)))


if __name__ == "__main__":
    main()
