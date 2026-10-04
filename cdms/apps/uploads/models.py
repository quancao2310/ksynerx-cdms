from django.db import models
from django.utils import timezone


class ExcelUpload(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Received"
        PROCESSING = "PROCESSING", "Processing"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        FAILED = "FAILED", "Failed"

    sha256 = models.CharField(max_length=64, unique=True)
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.RECEIVED)
    source_ts = models.DateTimeField(default=timezone.now)
    lease_until = models.DateTimeField(null=True, blank=True)

    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    created = models.PositiveIntegerField(default=0)
    updated = models.PositiveIntegerField(default=0)
    unchanged = models.PositiveIntegerField(default=0)
    stale = models.PositiveIntegerField(default=0)
    rejected = models.PositiveIntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)
    error = models.TextField(blank=True, default="")

    received_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
