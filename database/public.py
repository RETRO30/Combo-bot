############################################################################
## Django ORM Standalone Python Template
############################################################################
""" Here we'll import the parts of Django we need. """

# Turn off bytecode generation
import sys
sys.dont_write_bytecode = True

# Django specific settings
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database.settings')
import django
django.setup()

# Import your models for use in your script
from database.db.models import *

############################################################################
## START OF APPLICATION
############################################################################
