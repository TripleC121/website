"""
WSGI config for chesley_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.contrib import admin
from django.urls import path
from django.urls import include

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chesley_web.settings")

application = get_wsgi_application()

