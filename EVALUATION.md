# Evaluation

The adapted Kaggle loop is reproducible with `python3 scripts/generate_synthetic.py && python3 scripts/evaluate.py`.

## Dataset

40 synthetic digital PDFs, 10 monthly invoices from each of four suppliers. Each invoice has five product lines, normalized totals and occasional fees. Twelve known changes are planted: four price increases, four pack-size changes and four new fees. Description punctuation/wording also varies to exercise normalization. Ground truth is in `data/synthetic/ground_truth.csv`.

## Baseline result

See `artifacts/evaluation.json` for the machine-readable run. On the generated fixture set:

- structured field extraction: 100% (expected for the controlled fixture grammar)
- invoices reconciled: 40/40
- exact-SKU item matching: 100%
- planted-change recall: 91.7% (11/12)
- false-alert rate: 8.3% (1 false alert among 12 predicted change keys)
- unit tests: five passing tests covering normalization, pack conversion, reconciliation, alerting and uncertain matching

These figures are a code-regression baseline, not a claim about real invoices. The fixture format is intentionally easier than supplier PDFs and phone photos.

## Failure cases deliberately exposed

- An image-only or unfamiliar invoice returns a clear unsupported-format message rather than guessed numbers.
- A failed subtotal/total reconciliation reduces signal confidence.
- A description-only similarity score in the middle band enters the human-confirmation table.
- Different pack families cannot be normalized into an invented comparison.
- Ranking shows only five items, while preserving the total signal count in the API.

The next meaningful evaluation is at least 100 redacted, permissioned pages across 10 suppliers, with field-level scoring and manual adjudication.
