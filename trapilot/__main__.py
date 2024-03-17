#!/usr/bin/env python3
"""
__main__.py for Trapilot
To launch Trapilot as a module

> python -m trapilot (with Python >= 3.9)
"""

from trapilot import main
from trapilot.constants import DEFAULT_DB_DRYRUN_URL
from trapilot.persistence.models import init_db

if __name__ == "__main__":
    init_db(DEFAULT_DB_DRYRUN_URL)
    main.main()
