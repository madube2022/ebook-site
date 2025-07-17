"""
WSGI config for ebook_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Define the base directory (2 levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the .env file
load_dotenv(dotenv_path=BASE_DIR / '.env')

# Set the default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ebook_site.settings')

# Create the application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
