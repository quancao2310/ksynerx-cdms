from enum import StrEnum

FIELD_MAP = (
    ("productId", "product_id"),
    ("sku", "sku"),
    ("partnerSKU", "partner_sku"),
    ("productName", "product_name"),
    ("assetType", "asset_type"),
    ("hasSerial", "has_serial"),
    ("hasExpiration", "has_expiration"),
    ("color", "color"),
    ("size", "size"),
    ("description", "description"),
    ("isActive", "is_active"),
    ("units", "units"),
    ("categories", "categories"),
)


class ChangeStatus(StrEnum):
    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    STALE = "stale"
    REJECTED = "rejected"
