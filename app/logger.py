import logging
import sys

from app.config import settings

logging.basicConfig(
    stream=sys.stdout,
    level=settings.LOG_LEVEL.upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger("auth-service")
