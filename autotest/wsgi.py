"""
WSGI config for autotest project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import logging

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autotest.settings')

application = get_wsgi_application()
logger = logging.getLogger("autohandel")
logger.info("######## Autohandel: Applying migrations ########")
call_command("migrate")