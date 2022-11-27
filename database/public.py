import os
import sys

import django

# A crutch to avoid import issues
if os.path.abspath('..') not in sys.path:
    sys.path.append(os.path.abspath('..')) 

# Turn off bytecode generation
sys.dont_write_bytecode = True

# Django specific settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database.settings')
django.setup()

# Import your models for use in your script
from database.db.models import *