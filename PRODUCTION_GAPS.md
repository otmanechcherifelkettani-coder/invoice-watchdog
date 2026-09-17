# Production gaps

This build proves the comparison workflow, not production document ingestion.

1. **OCR/layout:** generic scanned invoices and phone photos need deskewing, OCR and supplier-template evaluation. Never infer a price from low-confidence OCR without review.
2. **Extraction:** columns, multi-page tables, VAT, credits and locale-specific decimal formats need schema validation.
3. **Matching:** supplier SKU is strongest. Description-only matches need a learned alias table and optional small-model candidate ranking. A model must never calculate price changes.
4. **Safety:** parser sandboxing, upload limits, malware scanning and file-type verification are absent.
5. **Accounting:** credits, rebates, contract price lists, tax inclusion and catch-weight goods need explicit policy.
6. **Operations:** no accounts, tenant isolation, backups, monitoring, billing or integrations.

Before real use, score at least 100 permissioned/redacted pages from 10 suppliers. Measure each field, matching precision/recall, false alerts and planted-change recall. Require review for uncertain pack/UOM, unreconciled totals and OCR confidence below the chosen threshold.
