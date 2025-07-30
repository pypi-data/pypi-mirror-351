#!/usr/bin/env python3
"""Entry point for the CLI."""

import sys

from whatxtract.waweb import main

try:
    main()
except KeyboardInterrupt:
    print('\n[!] Interrupted by user (Ctrl+C). Exiting gracefully.')
    sys.exit(0)
