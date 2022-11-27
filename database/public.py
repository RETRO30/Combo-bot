import os
import sys
from pathlib import Path

import django

# A crutch to avoid import issues
if str(Path(__file__).parent.parent.absolute()) not in sys.path:
    sys.path.append(str(Path(__file__).parent.parent.absolute()))

# Turn off bytecode generation
sys.dont_write_bytecode = True

# Django specific settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database.settings')
django.setup()

# Import your models for use in your script
from database.db.models import Admin, Executor,Task
