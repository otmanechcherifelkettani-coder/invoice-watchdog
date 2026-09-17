# Build / change / stop criteria

## Baseline
Exact supplier SKU plus normalized pack is the baseline matcher. Description similarity is allowed only as a candidate generator and routes low confidence to human review.

## Build next when
- planted-change recall is at least 90%
- false alerts are at most 10% on the evaluation set
- unit price, quantity and line total extraction are each at least 95%
- 3 of 5 restaurant/bookkeeper interviews confirm a recently missed increase or fee
- 2 will pay at least EUR 99 for an audit or pre-commit to EUR 39/month

## Change approach when
- pack/UOM extraction is below 90%: add supplier templates before any larger model
- matching errors dominate: capture confirmed aliases and compare candidate-ranking approaches
- scans dominate: bake off invoice-specific extraction against OCR on redacted pages

## Stop when
After 5 real discovery audits, fewer than 3 reveal a material missed change, or fewer than 2 buyers will pay. Also stop automation for any supplier whose invoices cannot reconcile reliably; offer review-only or exclude it.
