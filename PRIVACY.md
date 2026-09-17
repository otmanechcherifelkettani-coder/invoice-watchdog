# Privacy and deletion

V1 runs on the user's machine. Uploaded bytes are parsed in memory, are not persisted by the app, and are not sent to model or OCR providers. Clicking **Clear session** removes the browser and server session state; restarting the server also clears all sessions.

The repository contains synthetic fixtures only. Do not commit real invoices.

Production needs: authenticated per-tenant storage, encryption in transit/at rest, a short configurable deletion schedule, deletion verification, access/audit logs, subprocess isolation for parsers, malware scanning, explicit processor/subprocessor terms, regional hosting, backups with matching retention, and a documented incident path. Redact bank, tax and personal fields when they are not needed for price comparison.
