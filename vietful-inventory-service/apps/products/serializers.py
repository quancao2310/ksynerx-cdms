from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    categoryCode = serializers.ReadOnlyField(source="code")
    categoryName = serializers.ReadOnlyField(source="name")

    class Meta:
        model = Category
        fields = ['categoryCode', 'categoryName']


class ProductSerializer(serializers.ModelSerializer):
    productId = serializers.IntegerField(source="id", read_only=True)
    productName = serializers.CharField(source="name")
    partnerSKU = serializers.ReadOnlyField(source="partner_sku")
    assetType = serializers.ReadOnlyField(source="asset_type")
    hasSerial = serializers.ReadOnlyField(source="has_serial")
    hasExpiration = serializers.ReadOnlyField(source="has_expiration")
    isActive = serializers.ReadOnlyField(source="is_active")
    units = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "productId",
            "sku",
            "partnerSKU",
            "productName",
            "assetType",
            "hasSerial",
            "hasExpiration",
            "color",
            "size",
            "description",
            "isActive",
            "units",
            "categories",
        ]

    def get_units(self, obj):
        return sorted(obj.units)
