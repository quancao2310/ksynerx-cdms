from django.db.models import Prefetch
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView, Http404

from ..models import Category, Product
from ..serializers import ProductSerializer
from .pagination import ProductPagination


def product_queryset():
    return Product.objects.prefetch_related(
        Prefetch("categories", queryset=Category.objects.order_by("code"))
    ).order_by("id")

class ProductListView(ListCreateAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        return product_queryset()


class ProductDetailView(RetrieveUpdateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return product_queryset()
