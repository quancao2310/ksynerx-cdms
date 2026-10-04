import logging
import time

import requests
from apps.products.constants import ChangeStatus
from apps.products.models import ProductVersion
from apps.products.services import apply_change
from django.conf import settings
from django.utils import timezone

from .models import PollRun

logger = logging.getLogger(__name__)


class VietfulError(Exception):
    pass


def get_page(session: requests.Session, url, page_index):
    params = {
        "page_index": page_index,
        "page_size": settings.VIETFUL_PAGE_SIZE,
    }
    attempts = settings.VIETFUL_MAX_ATTEMPTS
    error = ""

    for attempt in range(1, attempts + 1):
        try:
            resp = session.get(url, params=params, timeout=settings.VIETFUL_TIMEOUT)
        except (requests.ConnectionError, requests.Timeout) as exc:
            error = f"network error: {type(exc).__name__}"
        else:
            if resp.status_code >= 500:
                error = f"HTTP {resp.status_code}"
            elif resp.status_code >= 400:
                raise VietfulError(f"HTTP {resp.status_code} for page {params.get('page_index')}")
            else:
                try:
                    return resp.json()
                except ValueError:
                    error = "invalid JSON"
        if attempt < attempts:
            time.sleep(settings.VIETFUL_BACKOFF_SECONDS * attempt)

    raise VietfulError(f"{error} on page {params.get('page_index')} (after {attempts} attempts)")


def fetch_product_pages():
    url = f"{settings.VIETFUL_BASE_URL}{settings.VIETFUL_PRODUCTS_PATH}"
    page_index = 1
    with requests.Session() as session:
        session.headers["Accept"] = "application/json"
        while True:
            body = get_page(session, url, page_index)
            yield body["results"]
            if not body.get("next"):
                return
            page_index += 1


def poll_once():
    run = PollRun.objects.create()
    source_ts = timezone.now()

    try:
        for items in fetch_product_pages():
            for item in items:
                result = apply_change(
                    source=ProductVersion.Source.POLL,
                    raw=item,
                    source_ts=source_ts,
                    source_ref=f"poll-run:{run.pk}",
                )
                field = result.status.value
                setattr(run, field, getattr(run, field) + 1)
                if result.status == ChangeStatus.REJECTED:
                    logger.warning("rejected item: %s", "; ".join(result.errors))
            run.fetched += len(items)
            run.save()
        run.status = PollRun.PollRunStatus.SUCCEEDED
    except Exception as exc:
        logger.exception("poll run %s failed", run.pk)
        run.status = PollRun.PollRunStatus.FAILED
        run.error = f"{type(exc).__name__}: {exc}"[:2000]

    run.finished_at = timezone.now()
    run.save()
    logger.info("poll run %s %s: fetched=%s", run.pk, run.status, run.fetched)
    return run
