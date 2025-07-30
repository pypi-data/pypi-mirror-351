"""
Custom exceptions for Beem SMS SDK
"""


class SMSError(Exception):
    """Base exception for SMS operations"""

    pass


class AuthenticationError(SMSError):
    """Authentication failed"""

    pass


class ValidationError(SMSError):
    """Input validation failed"""

    pass


class APIError(SMSError):
    """API request failed"""

    pass


class NetworkError(SMSError):
    """Network-related error"""

    pass
