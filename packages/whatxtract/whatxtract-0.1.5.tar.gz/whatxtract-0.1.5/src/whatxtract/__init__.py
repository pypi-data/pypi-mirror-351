"""
WhatXtract: WhatsApp data extraction and automation toolkit.

WhatsApp Contacts Extractor and Number Checker via WhatsApp Web
A WhatsApp data extraction and automation toolkit
"""

import importlib.metadata

__ = {}

try:
    __ = importlib.metadata.metadata(__name__)
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = '0.0.0'  # Fallback for development mode

# fmt: off
__project__     = "WhatXtract"
__title__       = __name__ or "whatxtract"
__version__     = __version__ or "0.0.0"
__summary__     = 'A WhatsApp data extraction and automation toolkit'
__description__ = 'A WhatsApp data extraction and automation toolkit'
__author__      = __.get("Author", "Hasan Rasel")
__email__       = __.get("Author-email", "rrss.mahmud@gmail.com")
__license__     = __.get("License", "MIT")
__url__         = "https://github.com/bitbytelab/whatxtract"
__copyright__   = "2025 BitByteLab"

f"""
Version: {__version__}
License: {__license__}
Author : {__author__}
Email  : {__email__}
URL    : {__url__}
Copyright © {__copyright__} 
"""
