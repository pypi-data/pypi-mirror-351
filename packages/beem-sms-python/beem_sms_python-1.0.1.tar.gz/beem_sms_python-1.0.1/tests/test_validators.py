"""
Unit tests for phone number validators
"""

import pytest

from beem_sms.validators import PhoneNumberValidator


class TestPhoneNumberValidator:
    """Test suite for PhoneNumberValidator"""

    @pytest.mark.parametrize(
        "phone_number,expected",
        [
            ("+255712345678", True),
            ("+255687654321", True),
            ("255712345678", True),
            ("0712345678", True),
            ("0687654321", True),
            ("+255 712 345 678", True),
            ("255-712-345-678", True),
            ("(255) 712 345 678", True),
            ("", False),
            ("123", False),
            ("+255512345678", False),
            ("712345678", True),
            ("+1234567890123456", False),
        ],
    )
    def test_validate(self, phone_number, expected):
        """Test phone number validation"""
        assert PhoneNumberValidator.validate(phone_number) == expected

    @pytest.mark.parametrize(
        "phone_number,expected",
        [
            ("0712345678", "+255712345678"),
            ("255712345678", "+255712345678"),
            ("+255712345678", "+255712345678"),
            ("255 712 345 678", "+255712345678"),
            ("255-712-345-678", "+255712345678"),
            ("(255) 712 345 678", "+255712345678"),
            ("712345678", "+255712345678"),
        ],
    )
    def test_clean(self, phone_number, expected):
        """Test phone number cleaning"""
        assert PhoneNumberValidator.clean(phone_number) == expected

    def test_validate_batch(self):
        """Test batch validation"""
        numbers = ["+255712345678", "invalid", "0687654321"]
        results = PhoneNumberValidator.validate_batch(numbers)
        assert results == [True, False, True]
