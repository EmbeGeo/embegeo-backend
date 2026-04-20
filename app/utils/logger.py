import logging
from datetime import datetime

from pythonjsonlogger import jsonlogger

from app.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


def setup_logging():
    logger = logging.getLogger()

    # Set default logging level from settings
    logger.setLevel(settings.LOG_LEVEL.upper())

    # Check if handlers already exist to prevent duplicate logs in reloaded environments
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Set log level for uvicorn access logs
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = []  # Remove default handlers
    uvicorn_access_logger.propagate = (
        False  # Prevent logs from propagating to root logger
    )
    uvicorn_access_logger.addHandler(handler)  # Add our custom handler

    return logger


# Initialize logger
logger = setup_logging()
