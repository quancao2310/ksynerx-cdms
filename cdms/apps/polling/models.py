from django.db import models
from django.utils import timezone


class PollRun(models.Model):
    class PollRunStatus(models.TextChoices):
        RUNNING = "RUNNING", "Running"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        FAILED = "FAILED", "Failed"

    status = models.CharField(
        max_length=10,
        choices=PollRunStatus.choices,
        default=PollRunStatus.RUNNING,
    )
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    fetched = models.PositiveIntegerField(default=0)
    created = models.PositiveIntegerField(default=0)
    updated = models.PositiveIntegerField(default=0)
    unchanged = models.PositiveIntegerField(default=0)
    stale = models.PositiveIntegerField(default=0)
    rejected = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True, default="")
