"""
Beem SMS Python SDK

A professional Python package for sending SMS via Beem API.
"""

__version__ = "1.0.1"
__author__ = "James Mashaka"
__email__ = "j1997ames@gmail.com"

from .client import BeemSMSClient, SMSEncoding, SMSRecipient, SMSResponse, send_sms
from .exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    SMSError,
    ValidationError,
)
from .validators import PhoneNumberValidator

__all__ = [
    "BeemSMSClient",
    "SMSResponse",
    "SMSRecipient",
    "SMSEncoding",
    "send_sms",
    "SMSError",
    "AuthenticationError",
    "ValidationError",
    "APIError",
    "NetworkError",
    "PhoneNumberValidator",
]
