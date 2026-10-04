import logging
import signal
import threading

from django import db
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import DatabaseError
from django.utils import timezone

from apps.polling.models import PollRun
from apps.polling.services import poll_once

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Query Vietful data via pre-defined scheduled intervals"

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true")

    def handle(self, *args, once=False, **options):
        stop = threading.Event()
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, lambda *_: stop.set())

        PollRun.objects.filter(status="RUNNING").update(
            status="FAILED", finished_at=timezone.now(), error="interrupted: process stopped")

        while not stop.is_set():
            try:
                db.close_old_connections()
                poll_once()
            except DatabaseError:
                logger.exception("database error; will retry at next interval")
                db.connections.close_all()
            if once:
                break
            stop.wait(settings.CDMS_POLL_INTERVAL_SECONDS)
