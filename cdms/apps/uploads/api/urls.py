from django.urls import path

from .views import ExcelUploadDetail, ExcelUploadList, ProductExcelUploadView

app_name = "uploads"

urlpatterns = [
    path("products/", ProductExcelUploadView.as_view(), name="upload-products"),
    path("", ExcelUploadList.as_view(), name="upload-list"),
    path("<int:pk>/", ExcelUploadDetail.as_view(), name="upload-detail"),
]
