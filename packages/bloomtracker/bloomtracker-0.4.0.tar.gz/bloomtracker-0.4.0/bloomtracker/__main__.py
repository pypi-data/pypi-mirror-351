#!/usr/bin/env python3
"""
Command-line interface for the dwdpollen package.
"""

import sys
from bloomtracker.cli import main

if __name__ == "__main__":
    main()  # main doesn't return an exit code
    sys.exit(0)
