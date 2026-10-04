from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("products/", include("apps.products.api.urls")),
    path("poll/", include("apps.polling.api.urls")),
    path("uploads/", include("apps.uploads.api.urls")),
]
