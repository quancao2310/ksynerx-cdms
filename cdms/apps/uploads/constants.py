REQUIRED_COLUMNS = (
    "productId",
    "sku",
    "productName",
    "assetType",
    "hasSerial",
    "hasExpiration",
    "isActive",
)
KNOWN_COLUMNS = REQUIRED_COLUMNS + (
    "partnerSKU",
    "color",
    "size",
    "description",
    "units",
    "categories",
)
TEXT_COLUMNS = ("sku", "partnerSKU", "productName", "assetType", "color", "size", "description")
BOOL_COLUMNS = ("hasSerial", "hasExpiration", "isActive")

MAX_STORED_ERRORS = 100
LEASE_SECONDS = 300
