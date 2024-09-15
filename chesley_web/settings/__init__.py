import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from .base import *  # noqa: F403

environment = os.environ.get(
    "DJANGO_SETTINGS_MODULE", "chesley_web.settings.development"
)
logger.debug(f"DJANGO_SETTINGS_MODULE: {environment}")

if environment == "chesley_web.settings.production":
    logger.debug("Loading production settings")
    from .production import *  # noqa: F403, F401
else:
    logger.debug("Loading development settings")
    from .development import *  # noqa: F403, F401
