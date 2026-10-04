from django.conf import settings
from rest_framework import serializers

from .models import ExcelUpload


class ExcelUploadRequestSerializer(serializers.Serializer):
    file = serializers.FileField(max_length=255)

    def validate_file(self, file):
        if not file.name.lower().endswith(".xlsx"):
            raise serializers.ValidationError("Only .xlsx files are supported")
        if file.size > settings.CDMS_UPLOAD_MAX_BYTES:
            raise serializers.ValidationError("File is too large")
        return file


class ExcelUploadSerializer(serializers.ModelSerializer):
    sourceTs = serializers.DateTimeField(source="source_ts", read_only=True)
    totalRows = serializers.IntegerField(source="total_rows", read_only=True)
    processedRows = serializers.IntegerField(source="processed_rows", read_only=True)
    receivedAt = serializers.DateTimeField(source="received_at", read_only=True)
    finishedAt = serializers.DateTimeField(source="finished_at", read_only=True)

    class Meta:
        model = ExcelUpload
        fields = [
            "id",
            "sha256",
            "filename",
            "status",
            "sourceTs",
            "totalRows",
            "processedRows",
            "created",
            "updated",
            "unchanged",
            "stale",
            "rejected",
            "errors",
            "error",
            "receivedAt",
            "finishedAt",
        ]
        read_only_fields = fields
