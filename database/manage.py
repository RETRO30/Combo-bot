#!/usr/bin/env python
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # A crutch to avoid import issues
    if str(Path(__file__).parent.parent.absolute()) not in sys.path:
        sys.path.append(str(Path(__file__).parent.parent.absolute()))


    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
