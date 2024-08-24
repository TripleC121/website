import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from .base import *  # noqa: F403

environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')
logger.debug(f"DJANGO_ENVIRONMENT: {environment}")
logger.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

if environment == 'production':
    logger.debug("Loading production settings")
    from .production import *  # noqa: F403, F401
else:
    logger.debug("Loading development settings")
    from .development import *  # noqa: F403, F401
