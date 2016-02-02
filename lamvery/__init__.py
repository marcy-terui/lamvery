"""
lamvery
----
Function based deploy and management tool for AWS Lambda.
"""

__version__ = '0.10.1'

import importlib

secret = importlib.import_module('lamvery.secret')
