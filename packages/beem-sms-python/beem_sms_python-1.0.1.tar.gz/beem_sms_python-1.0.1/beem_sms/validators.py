"""
Input validation utilities for Beem SMS SDK
"""

import re
from typing import List


class PhoneNumberValidator:
    """Phone number validation utilities"""

    PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{7,14}$")

    TANZANIA_PATTERNS = [
        re.compile(r"^\+255[67]\d{8}$"),
        re.compile(r"^255[67]\d{8}$"),
        re.compile(r"^0[67]\d{8}$"),
        re.compile(r"^[67]\d{8}$"),
    ]

    @classmethod
    def validate(cls, phone_number: str) -> bool:
        """Validate phone number format"""
        if not phone_number:
            return False

        cleaned = re.sub(r"[\s\-\(\)]", "", phone_number)

        # Check if it's a Tanzania number first
        if (
            cleaned.startswith("+255")
            or cleaned.startswith("255")
            or cleaned.startswith("0")
            or (len(cleaned) == 9 and cleaned[0] in "67")
        ):
            # Use Tanzania-specific validation for Tanzania numbers
            return any(pattern.match(cleaned) for pattern in cls.TANZANIA_PATTERNS)

        # For non-Tanzania numbers, use general international format
        return bool(cls.PHONE_PATTERN.match(cleaned))

    @classmethod
    def clean(cls, phone_number: str) -> str:
        """Clean and format phone number to international format"""
        cleaned = re.sub(r"[\s\-\(\)]", "", phone_number)

        if cleaned.startswith("0"):
            cleaned = f"+255{cleaned[1:]}"
        elif cleaned.startswith("255") and not cleaned.startswith("+"):
            cleaned = f"+{cleaned}"
        elif len(cleaned) == 9 and cleaned[0] in "67":
            cleaned = f"+255{cleaned}"
        elif not cleaned.startswith("+"):
            cleaned = f"+255{cleaned}"

        return cleaned

    @classmethod
    def validate_batch(cls, phone_numbers: List[str]) -> List[bool]:
        """Validate a batch of phone numbers"""
        return [cls.validate(number) for number in phone_numbers]
