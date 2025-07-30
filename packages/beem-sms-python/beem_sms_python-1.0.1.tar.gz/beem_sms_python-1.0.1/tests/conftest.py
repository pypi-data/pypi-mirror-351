"""
Pytest configuration and fixtures
"""

from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_response():
    """Create mock HTTP response"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"request_id": "test_123"}
    response.content = b'{"request_id": "test_123"}'
    response.headers = {}
    response.text = '{"request_id": "test_123"}'
    return response


@pytest.fixture
def sample_recipients():
    """Sample phone numbers for testing"""
    return ["+255712345678", "+255687654321", "+255798765432"]
