from rest_framework import serializers

from .models import Product, ProductVersion


class ProductSerializer(serializers.ModelSerializer):
    productId = serializers.IntegerField(source="product_id", read_only=True)
    partnerSKU = serializers.CharField(source="partner_sku", read_only=True, allow_null=True)
    productName = serializers.CharField(source="product_name", read_only=True)
    assetType = serializers.CharField(source="asset_type", read_only=True)
    hasSerial = serializers.BooleanField(source="has_serial", read_only=True)
    hasExpiration = serializers.BooleanField(source="has_expiration", read_only=True)
    isActive = serializers.BooleanField(source="is_active", read_only=True)
    lastChangedAt = serializers.DateTimeField(source="last_changed_at", read_only=True)

    class Meta:
        model = Product
        fields = (
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
            "version",
            "lastChangedAt",
        )
        read_only_fields = fields


class ProductVersionSerializer(serializers.ModelSerializer):
    sourceRef = serializers.CharField(source="source_ref", read_only=True)
    sourceTs = serializers.DateTimeField(source="source_ts", read_only=True)
    changedFields = serializers.JSONField(source="changed_fields", read_only=True)

    class Meta:
        model = ProductVersion
        fields = (
            "version",
            "source",
            "sourceRef",
            "sourceTs",
            "changedFields",
            "data",
        )
        read_only_fields = fields
