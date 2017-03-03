"""
lamvery
----
Function based deploy and management tool for AWS Lambda.
"""

__version__ = '0.18.2'

import importlib

secret = importlib.import_module('lamvery.secret')
env = importlib.import_module('lamvery.env')
