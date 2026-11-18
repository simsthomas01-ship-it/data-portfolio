# Data portfolio

Small data projects in SQL and Python. Live write-up: the Projects page of The Crusty Crab site.

## 1. Auto claims practice database and dashboard
A synthetic personal-auto book of business (6 tables, 241 rows; nothing is real).

- `sql/claims_practice_setup.sql` - creates and fills the database (SQLite).
- `docs/questions.md` - 38 practice questions, from basic SELECTs to window functions.
- `docs/answer_key.md` - worked answers.
- `analysis/build_claims_dashboard.py` - runs the dashboard queries (joins, aggregates, loss ratio) and writes one JSON file for the charts.

Try it: `python3 analysis/build_claims_dashboard.py` (standard library only; writes `output/claims-data.json`).

## 2. Billboard Hot 100 matching
`analysis/hot100_matching.py` - weekly job that cleans artist and title names (accents, punctuation, featured credits) and fuzzy-matches the chart against a music library with a similarity score. Standard library only. Credentials are typed in at setup and never stored in this repo.
