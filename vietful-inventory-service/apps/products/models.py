from django.contrib.postgres.fields import ArrayField
from django.db import models


class Category(models.Model):
    name = models.CharField("category name", max_length=100)
    code = models.CharField("category code", unique=True, max_length=100)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(models.Model):
    class AssetType(models.TextChoices):
        SINGLE = "Single", "Single"
        BUNDLE = "Bundle", "Bundle"
        MULTIPLE_BARCODES = "MultipleBarcodes", "Multiple Barcodes"

    name = models.CharField("product name", max_length=255)
    description = models.TextField("description", null=True, blank=True)
    sku = models.CharField("SKU", max_length=50, unique=True)
    partner_sku = models.CharField("partner SKU", max_length=50, null=True, blank=True)
    asset_type = models.CharField(
        "asset type",
        max_length=20,
        choices=AssetType.choices,
        default=AssetType.SINGLE,
    )
    has_serial = models.BooleanField("has serial", default=False)
    has_expiration = models.BooleanField("has expiration date", default=False)
    color = models.CharField("color", max_length=50, blank=True, null=True)
    size = models.CharField("size", max_length=50, blank=True, null=True)
    is_active = models.BooleanField("is active", default=True)
    units = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
    )
    created_at = models.DateTimeField("created at", auto_now_add=True, editable=False)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="products",
        verbose_name="categories",
    )

    def __str__(self):
        return f"{self.sku} - {self.name}"
