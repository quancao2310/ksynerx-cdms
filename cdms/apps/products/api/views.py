from apps.products.models import Product, ProductVersion
from apps.products.serializers import ProductSerializer, ProductVersionSerializer
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.order_by("product_id")


class ProductDetailView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductVersionsView(ListAPIView):
    serializer_class = ProductVersionSerializer

    def get_queryset(self):
        get_object_or_404(Product, pk=self.kwargs["pk"])
        return ProductVersion.objects.filter(product_id=self.kwargs["pk"]).order_by("version")
