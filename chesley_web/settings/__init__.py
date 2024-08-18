import os
from .base import *  # noqa: F403

environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *  # noqa: F403, F401
else:
    from .development import *  # noqa: F403, F401

# Optionally, you can add a print statement for debugging:
# print(f"Running in {environment} environment")