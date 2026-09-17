# Supplier Invoice Watchdog v1

A local-first proof of concept that compares supplier invoices and surfaces price creep, pack-size changes, fuel surcharges and market adjustments with source citations.

This is a deliberately small decision-support demo. It does **not** contact suppliers, make accounting entries, or upload documents anywhere.

## Quick start

Requires Python 3.10+.

```bash
python3 scripts/generate_synthetic.py   # reproducible fixtures and ground truth
python3 app.py                          # open http://127.0.0.1:8000
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
- ranks the five highest-value changes and cites invoice, page and line
- keeps processing in memory and exposes a one-click session clear action

## Architecture

`app.py` serves a zero-build local web UI using the Python standard library. `watchdog/core.py` owns parsing, deterministic matching, reconciliation, signal detection and evaluation. JavaScript only renders state and supports reviewer edits. An AI matcher is a future adapter, never part of arithmetic or thresholds.

See `EVALUATION.md`, `PRIVACY.md`, `PRODUCTION_GAPS.md`, and `DECISIONS.md`.
