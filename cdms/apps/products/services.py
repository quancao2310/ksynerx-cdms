import hashlib
import json
import unicodedata
from copy import deepcopy
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.products.constants import ChangeStatus

from .models import Product, ProductVersion


class NormalizationError(Exception):
    def __init__(self, errors: dict[str, list[str]]):
        self.errors = deepcopy(errors)
        message = "; ".join(
            f"{field}: {error}"
            for field, messages in self.errors.items()
            for error in messages
        )
        super().__init__(message)


class ProductNormalizationService:
    @classmethod
    def normalize(cls, raw) -> dict:
        if not isinstance(raw, dict):
            raise NormalizationError({"payload": ["must be a JSON object"]})

        errors = {}
        data = {
            "productId": cls.parse_product_id(raw.get("productId"), errors),
            "sku": cls.clean_text(raw.get("sku"), "sku", errors, required=True),
            "partnerSKU": cls.clean_text(raw.get("partnerSKU"), "partnerSKU", errors),
            "productName": cls.clean_text(raw.get("productName"), "productName", errors, required=True),
            "assetType": cls.clean_text(raw.get("assetType"), "assetType", errors, required=True),
            "hasSerial": cls.parse_bool(raw.get("hasSerial"), "hasSerial", errors),
            "hasExpiration": cls.parse_bool(raw.get("hasExpiration"), "hasExpiration", errors),
            "color": cls.clean_text(raw.get("color"), "color", errors),
            "size": cls.clean_text(raw.get("size"), "size", errors),
            "description": cls.clean_text(raw.get("description"), "description", errors),
            "isActive": cls.parse_bool(raw.get("isActive"), "isActive", errors),
            "units": cls.parse_units(raw.get("units"), errors),
            "categories": cls.parse_categories(raw.get("categories"), errors),
        }

        if errors:
            raise NormalizationError(errors)

        return data

    @staticmethod
    def state_hash(data: dict):
        encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    @staticmethod
    def diff_data(old: dict, new: dict):
        return {
            key: {
                "old": old.get(key),
                "new": new.get(key)
            }
            for key in sorted(set(old) | set(new))
            if old.get(key) != new.get(key)
        }

    @classmethod
    def add_error(cls, errors, field, message):
        errors.setdefault(field, []).append(message)

    @classmethod
    def clean_text(cls, value, field, errors, required=False):
        if value is None:
            text = None
        elif isinstance(value, str):
            text = unicodedata.normalize("NFC", value).strip() or None
        else:
            cls.add_error(errors, field, "must be a string")
            return None

        if text is None and required:
            cls.add_error(errors, field, "is required")
        return text

    @classmethod
    def parse_bool(cls, value, field, errors):
        if isinstance(value, bool):
            return value

        if value is None:
            cls.add_error(errors, field, "is required")
        else:
            cls.add_error(errors, field, "must be a boolean")
        return None

    @classmethod
    def parse_product_id(cls, value, errors):
        if type(value) is int:
            return value
        cls.add_error(errors, "productId", "must be a positive integer")
        return None

    @classmethod
    def parse_units(cls, value, errors):
        if value is None:
            return []
        if not isinstance(value, list):
            cls.add_error(errors, "units", "must be an array of strings")
            return []
        result = set()
        for idx, item in enumerate(value):
            text = cls.clean_text(item, f"units[{idx}]", errors)
            if text:
                result.add(text)
        return sorted(result)

    @classmethod
    def parse_categories(cls, value, errors):
        if value is None:
            return []
        if not isinstance(value, list):
            cls.add_error(errors, "categories", "must be an array of objects")
            return []

        result = []
        for idx, item in enumerate(value):
            if not isinstance(item, dict):
                cls.add_error(errors, f"categories[{idx}]", "must be an object")
                continue
            code = cls.clean_text(item.get("categoryCode"), f"categories[{idx}].categoryCode", errors, required=True)
            name = cls.clean_text(item.get("categoryName"), f"categories[{idx}].categoryName", errors, required=True)
            if code is None or name is None:
                continue
            result.append({"categoryCode": code, "categoryName": name})

        return sorted(result, key=lambda c: c["categoryCode"])


@dataclass(frozen=True)
class Result:
    status: ChangeStatus
    errors: tuple[str, ...] = ()


def apply_change(source, raw, source_ts, source_ref=""):
    try:
        data = ProductNormalizationService.normalize(raw)
    except NormalizationError as exc:
        return Result(ChangeStatus.REJECTED, tuple(
            f"{field}: {message}" for field, messages in exc.errors.items() for message in messages
        ))

    product_id = data["productId"]
    new_hash = ProductNormalizationService.state_hash(data)

    current = Product.objects.filter(pk=product_id).values_list("content_hash", "last_source_ts").first()
    if current and current[0] == new_hash:
        return Result(ChangeStatus.STALE if source_ts < current[1] else ChangeStatus.UNCHANGED)

    now = timezone.now()
    with transaction.atomic():
        product = Product.objects.select_for_update().filter(pk=product_id).first()
        if product is None:
            product = Product(content_hash=new_hash, version=1, last_source_ts=source_ts, last_changed_at=now)
            product.set_data(data)
            product.save()
            changed = {}
            status = ChangeStatus.CREATED
        else:
            if source_ts < product.last_source_ts:
                return Result(ChangeStatus.STALE)
            if product.content_hash == new_hash:
                return Result(ChangeStatus.UNCHANGED)
            changed = ProductNormalizationService.diff_data(product.as_data(), data)
            status = ChangeStatus.UPDATED
            product.set_data(data)
            product.content_hash = new_hash
            product.version += 1
            product.last_source_ts = source_ts
            product.last_changed_at = now
            product.save()

        ProductVersion.objects.create(
            product=product,
            version=product.version,
            content_hash=new_hash,
            data=data,
            changed_fields=changed,
            source=source,
            source_ref=source_ref,
            source_ts=source_ts,
            recorded_at=now,
        )

    return Result(status)
