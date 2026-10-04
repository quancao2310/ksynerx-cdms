from apps.uploads.models import ExcelUpload
from apps.uploads.serializers import ExcelUploadRequestSerializer, ExcelUploadSerializer
from apps.uploads.services import ExcelUploadService, InvalidWorkbook, UploadBusy
from django.db import DatabaseError
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView


class ProductExcelUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        request_serializer = ExcelUploadRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        file = request_serializer.validated_data["file"]

        try:
            upload, is_new = ExcelUploadService.upload(file.name, file.read())
            upload = ExcelUploadService.process(upload.pk)
        except InvalidWorkbook as exc:
            raise serializers.ValidationError({"file": [str(exc)]})
        except UploadBusy:
            return Response(
                {"detail": "This file is already being processed"},
                status=status.HTTP_409_CONFLICT,
            )
        except DatabaseError:
            return Response(
                {"detail": "Database unavailable, retry the same file later"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            ExcelUploadSerializer(upload).data,
            status=status.HTTP_201_CREATED if is_new else status.HTTP_200_OK,
        )


class ExcelUploadList(ListAPIView):
    serializer_class = ExcelUploadSerializer
    queryset = ExcelUpload.objects.order_by("-id")


class ExcelUploadDetail(RetrieveAPIView):
    serializer_class = ExcelUploadSerializer
    queryset = ExcelUpload.objects.all()
