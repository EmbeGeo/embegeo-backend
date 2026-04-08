# Define constants here
# Example:
# DEFAULT_PAGINATION_LIMIT = 20
# MAX_PAGINATION_LIMIT = 100

# OCR Data Statuses
OCR_STATUS_VALID = "valid"
OCR_STATUS_INVALID = "invalid"
OCR_STATUS_PENDING = "pending"

# Redis Cache Keys
REDIS_KEY_LATEST_OCR_DATA = "latest_ocr_data"
REDIS_EXPIRE_LATEST_OCR_DATA_SECONDS = 3600  # 1 hour
