# Supplier Invoice Watchdog v1

A proof of concept that compares supplier invoices, reveals a headline estimate of possible price creep, and shows the exact price, pack-size and fee evidence behind it.

This is a deliberately small decision-support demo. It does **not** contact suppliers, make accounting entries, or upload documents anywhere.

## Hosted demo

A hosted instance of this demo runs on Render's free web service, deployed from this repository (`pip install -r requirements.txt`, then `python app.py`; the app reads `PORT` from the environment). It is a **synthetic demo on a public server**: use the built-in demo data and do not upload real invoices. The upload path exists to show product behavior only; see `PRIVACY.md` and `PRODUCTION_GAPS.md` before any real use.

## Quick start

Requires Python 3.10+.

```bash
python3 scripts/generate_synthetic.py   # reproducible fixtures and ground truth
python3 app.py                          # open http://localhost:8000
```

Click **Load demo audit**, or upload 4+ generated PDFs from `data/synthetic/invoices/`.

Run tests and evaluation:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/evaluate.py
```

No paid credentials or network calls are required. PDF parsing uses `pypdf` when installed; the included fixture sidecars provide an offline fallback. Phone-photo uploads are accepted, but generic OCR is intentionally a production gap (see `PRODUCTION_GAPS.md`).

## What v1 does

- extracts supplier, invoice/date, rows, pack/UOM, quantity, unit price, fees and totals from the synthetic fixture format
- normalizes descriptions and pack units with deterministic rules
- matches same-SKU products first, then token/pack similarity
- sends uncertain matches to an editable review table
- verifies invoice arithmetic and reduces confidence when totals do not reconcile
- reveals a free headline estimate from positive changes found in the compared periods
- previews a detailed evidence layer with supplier, old vs new price or fee, invoice line, and estimated monthly impact
- ranks the five highest-value changes and cites invoice, page and line
- keeps processing in memory and exposes a one-click session clear action

## Architecture

`app.py` serves a zero-build local web UI using the Python standard library. `watchdog/core.py` owns parsing, deterministic matching, reconciliation, signal detection and evaluation. JavaScript only renders state and supports reviewer edits. An AI matcher is a future adapter, never part of arithmetic or thresholds.

See `EVALUATION.md`, `PRIVACY.md`, `PRODUCTION_GAPS.md`, and `DECISIONS.md`.
