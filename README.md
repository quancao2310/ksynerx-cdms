# CDMS - Change Data Management Service (prototype)

A prototype service that stores only new or changed product data from an emulated inventory system (Vietful Inventory Service).

## Technology Stack

- Language: Python
- Back-end: Django, Django REST Framework
- Database: PostgreSQL
- Containerization: Docker

## Components

- `vietful-inventory-service/`: Vietful emulator that exposes Products APIs (`/api/v1/products/`).
- `cdms/`: the CDMS itself. `cdms-web` serves the read API and Excel upload; `cdms-poller` runs scheduled polling.
- Two PostgreSQL instances, one per service (`postgres-vietful`, `postgres-cdms`).

## Design: store only changes, exactly once

- Each product commits on its own with its own key (`productId`), so one bad row does not block the rest.
- Every source (polling, Excel upload) goes through one write function - `apply_change` with idempotent processing:

  1. Normalize the payload (trimming, sorted/deduplicated `units` and `categories`, etc.). Invalid input is rejected.
  2. Hash the normalized data and compare it with the product's current state.
  3. Reject stale data: if `source_ts` is older than the product's `last_source_ts`, the change is `stale`.
  4. Write atomically: Use `SELECT ... FOR UPDATE` on the product, then update `Product` and insert a `ProductVersion` row in one transaction. Added a unique constraint on product and version for integrity check.

## Implemented data processing mechanisms

### Scheduled polling

- `python manage.py run_poller` loops: reads Vietful page by page until `next` is empty.
- Each run is recorded as a `PollRun`.
- A failed page marks the run `FAILED`; earlier pages are kept and the next run is idempotent.
- SIGTERM stops the loop gracefully.
- Fetch the poll run history: `GET /api/v1/poll/runs/`.

### Excel upload

```
curl -F "file=@products.xlsx" http://localhost:8001/api/v1/uploads/products/
GET /api/v1/uploads/            list uploads
GET /api/v1/uploads/<id>/       status, counters, per-row errors
```

- Submit `.xlsx` file upto 10 MB.
- Required headers: `productId, sku, productName, assetType, hasSerial, hasExpiration, isActive`.
- Optional headers: `partnerSKU, color, size, description, units, categories`.

Durability and consistency:
- The file is written to disk first as `<MEDIA_ROOT>/uploads/<sha256>.xlsx`, only then is the `ExcelUpload` record committed and rows processed.
- Files are deduplicated by sha256: re-uploading a finished file returns 200 with the earlier result and creates no versions.
- Rows are processed in chunks. If the process dies, uploading the same file again resumes from the cursor. Replaying rows is safe because `apply_change` is idempotent.
- Invalid rows are `rejected` and listed in `errors` (max 100); other rows are still applied.

## Installation

- Install Docker and Docker Compose
- Set up `.env` files
  - `.envs/.postgres-cdms.env`
  - `.envs/.postgres-vietful.env`
  - `cdms/.env`
  - `vietful-inventory-service/.env`
- Run `docker compose up -d`

## Design decisions and limitations

- No Celery: correctness comes from the transaction and hash, not a queue, and a broker would only add failure points for one periodic job. Hence a single polling worker, no advisory lock, no dead-letter handling.
- Vietful has no `updatedAt`, so ordering uses timestamps assigned by CDMS. All sources are peers and the last writer wins by `source_ts`, so Excel data can be overwritten by the next poll.
- Excel upload is synchronous: the response carries the final result and nothing can fail between "accepted" and "applied". Very large files may time out (re-uploading resumes); an async 202 variant is a possible improvement.
- A request that outlives its 5-minute lease may be processed concurrently with another: data stays correct, counters may double count.
- Uploaded files are never deleted, the API has no authentication, and the real Vietful spec was not fully checked.

## Done / not done

Done:
- Vietful emulator for products data and Faker seeding.
- Scheduled polling
- Excel upload
- The change-only write path with hashing, stale-data detection, row locking and versioning.

Not done:
- Process data via Webhook callbacks
- Spike and concurrent-mechanism load tests
- Automated tests: the `tests.py` files are stubs

## Lessons learned

- "Exactly once" is at-least-once plus idempotency.
- Do not wrap a whole poll or a whole file in one transaction: it holds locks and DB connections while waiting on HTTP, and loses everything on failure. Small commits with a progress cursor allow safe resume.
- File-level (sha256) and content-level (hash) deduplication solve different problems; both are needed.
- Without an `updatedAt` from the source, ordering must rely on self-assigned timestamps, with last-writer-wins as the consequence.
