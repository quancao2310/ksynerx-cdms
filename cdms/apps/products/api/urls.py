from django.urls import path

from .views import ProductDetailView, ProductListView, ProductVersionsView

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view()),
    path("<int:pk>/", ProductDetailView.as_view()),
    path("<int:pk>/versions/", ProductVersionsView.as_view()),
]
