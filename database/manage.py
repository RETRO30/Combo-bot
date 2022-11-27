#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    # A crutch to avoid import issues
    if os.path.abspath('..') not in sys.path:
        sys.path.append(os.path.abspath('..')) 


    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
