from __future__ import annotations

from .router import route, lambda_handler, api_handler
from .response import create_response, ResponseData
from .request import HTTPRequest


__version__ = "1.0.0"
__author__ = "Abdulkarim Essam"
__email__ = "abdulkarim.essam@hotmail.com"

__all__ = [
    # Core routing functions
    "route",
    "lambda_handler",
    "api_handler",
    # Request/Response utilities
    "create_response",
    "HTTPRequest",
    # Type aliases for users
    "ResponseData",
    # Package metadata
    "__version__",
    "__author__",
    "__email__",
]