"""
WSGI config for library project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Add your project directory to the sys.path
path = '/home/unimaidLibrary/config'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Activate your virtual environment (optional but recommended)
activate_env = '/home/unimaidLibrary/myenv/bin/activate_ths.py'
if os.path.exists(activate_env):
    with open(activate_env) as f:
        exec(f.read(), {'__file__': activate_env})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
