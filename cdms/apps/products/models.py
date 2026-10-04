from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone

from .constants import FIELD_MAP


class Product(models.Model):
    product_id = models.BigIntegerField("product id", primary_key=True)
    sku = models.TextField("SKU", unique=True)
    partner_sku = models.TextField("partner SKU", null=True, blank=True)
    product_name = models.TextField("product name")
    asset_type = models.TextField("asset type")
    has_serial = models.BooleanField("has serial")
    has_expiration = models.BooleanField("has expiration date")
    color = models.TextField("color", null=True, blank=True)
    size = models.TextField("size", null=True, blank=True)
    description = models.TextField("description", null=True, blank=True)
    is_active = models.BooleanField("is active")
    units = ArrayField(
        models.TextField("unit"),
        blank=True,
        default=list,
    )
    categories = models.JSONField("categories", default=list)
    content_hash = models.CharField("content hash", max_length=64)
    version = models.PositiveIntegerField("version")
    last_source_ts = models.DateTimeField("last source timestamp")
    last_changed_at = models.DateTimeField("last changed at", default=timezone.now)

    def as_data(self):
        return {api: getattr(self, attr) for api, attr in FIELD_MAP}

    def set_data(self, data):
        for api, attr in FIELD_MAP:
            setattr(self, attr, data[api])

    def __str__(self):
        return f"{self.product_id} - {self.sku}"


class ProductVersion(models.Model):
    class Source(models.TextChoices):
        POLL = "POLL"
        WEBHOOK = "WEBHOOK"
        EXCEL = "EXCEL"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="versions")
    version = models.PositiveIntegerField("version")
    content_hash = models.CharField("content hash", max_length=64)
    data = models.JSONField("data", encoder=DjangoJSONEncoder)
    changed_fields = models.JSONField("changed fields", default=dict)
    source = models.CharField("source", max_length=10, choices=Source.choices)
    source_ref = models.CharField("source reference", max_length=100, blank=True, default="")
    source_ts = models.DateTimeField("source timestamp")
    recorded_at = models.DateTimeField("recorded at", default=timezone.now)

    class Meta:
        ordering = ["product_id", "version"]
        constraints = [models.UniqueConstraint(fields=["product", "version"], name="uq_product_version")]

    def __str__(self):
        return f"{self.product_id} - {self.product.sku} v{self.version}"
