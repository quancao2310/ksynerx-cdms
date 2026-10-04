from rest_framework import serializers

from .models import PollRun


class PollRunSerializer(serializers.ModelSerializer):
    startedAt = serializers.DateTimeField(source="started_at", read_only=True)
    finishedAt = serializers.DateTimeField(source="finished_at", read_only=True)

    class Meta:
        model = PollRun
        fields = [
            "id",
            "status",
            "startedAt",
            "finishedAt",
            "fetched",
            "created",
            "updated",
            "unchanged",
            "stale",
            "rejected",
            "error",
        ]
        read_only_fields = fields
