"""
Unit tests for BeemSMSClient
"""

from unittest.mock import Mock, patch

import pytest
import requests

from beem_sms import (
    APIError,
    AuthenticationError,
    BeemSMSClient,
    NetworkError,
    SMSEncoding,
    SMSRecipient,
    ValidationError,
)

# Use test credentials for unit tests
TEST_API_KEY = "test_api_key"
TEST_SECRET_KEY = "test_secret_key"
TEST_SOURCE_ADDR = "TestApp"
TEST_PHONE = "+255712345678"


class TestBeemSMSClient:
    """Test suite for BeemSMSClient"""

    @pytest.fixture
    def client(self):
        """Create test client instance"""
        return BeemSMSClient(api_key=TEST_API_KEY, secret_key=TEST_SECRET_KEY)

    def test_client_initialization(self):
        """Test client initialization with valid credentials"""
        client = BeemSMSClient(TEST_API_KEY, TEST_SECRET_KEY)
        assert client.api_key == TEST_API_KEY
        assert client.secret_key == TEST_SECRET_KEY
        assert client.base_url == BeemSMSClient.DEFAULT_BASE_URL

    def test_client_initialization_invalid_credentials(self):
        """Test client initialization with invalid credentials"""
        with pytest.raises(AuthenticationError):
            BeemSMSClient("", "secret_key")

        with pytest.raises(AuthenticationError):
            BeemSMSClient("api_key", "")

    def test_message_validation_empty(self, client):
        """Test message validation with empty message"""
        with pytest.raises(ValidationError, match="Message cannot be empty"):
            client._validate_message("", SMSEncoding.PLAIN_TEXT)

    def test_message_validation_too_long(self, client):
        """Test message validation with too long message"""
        long_message = "x" * (BeemSMSClient.MAX_MESSAGE_LENGTH + 1)
        with pytest.raises(ValidationError, match="Message too long"):
            client._validate_message(long_message, SMSEncoding.PLAIN_TEXT)

    def test_recipients_validation_empty(self, client):
        """Test recipients validation with empty list"""
        with pytest.raises(ValidationError, match="At least one recipient is required"):
            client._validate_recipients([])

    def test_recipients_validation_invalid_phone(self, client):
        """Test recipients validation with invalid phone number"""
        recipients = [SMSRecipient("invalid_phone")]
        with pytest.raises(ValidationError, match="Invalid phone number format"):
            client._validate_recipients(recipients)

    @patch("beem_sms.client.requests.Session.post")
    def test_send_sms_success(self, mock_post, client):
        """Test successful SMS sending"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"request_id": "test_123"}
        mock_response.content = b'{"request_id": "test_123"}'
        mock_response.headers = {}
        mock_post.return_value = mock_response

        response = client.send_sms(
            source_addr=TEST_SOURCE_ADDR, dest_addr=TEST_PHONE, message="Test message"
        )

        assert response.success is True
        assert response.status_code == 200
        assert response.request_id == "test_123"
        assert "successfully" in response.message

    @patch("beem_sms.client.requests.Session.post")
    def test_send_sms_authentication_error(self, mock_post, client):
        """Test SMS sending with authentication error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {}
        mock_response.content = b"{}"
        mock_response.headers = {}
        mock_post.return_value = mock_response

        with pytest.raises(AuthenticationError):
            client.send_sms(
                source_addr=TEST_SOURCE_ADDR,
                dest_addr=TEST_PHONE,
                message="Test message",
            )

    @patch("beem_sms.client.requests.Session.post")
    def test_send_sms_rate_limit(self, mock_post, client):
        """Test SMS sending with rate limit error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {}
        mock_response.content = b"{}"
        mock_response.headers = {}
        mock_post.return_value = mock_response

        with pytest.raises(APIError, match="Rate limit exceeded"):
            client.send_sms(
                source_addr=TEST_SOURCE_ADDR,
                dest_addr=TEST_PHONE,
                message="Test message",
            )

    @patch("beem_sms.client.requests.Session.post")
    def test_send_sms_network_timeout(self, mock_post, client):
        """Test SMS sending with network timeout"""
        mock_post.side_effect = requests.exceptions.Timeout()

        with pytest.raises(NetworkError, match="Request timeout"):
            client.send_sms(
                source_addr=TEST_SOURCE_ADDR,
                dest_addr=TEST_PHONE,
                message="Test message",
            )

    @patch("beem_sms.client.requests.Session.post")
    def test_send_bulk_sms(self, mock_post, client):
        """Test bulk SMS sending"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"request_id": "bulk_123"}
        mock_response.content = b'{"request_id": "bulk_123"}'
        mock_response.headers = {}
        mock_post.return_value = mock_response

        recipients = ["+255712345678", "+255687654321", "+255798765432"]

        results = client.send_bulk_sms(
            source_addr=TEST_SOURCE_ADDR,
            recipients=recipients,
            message="Bulk test message",
            batch_size=2,
        )

        assert len(results) == 2
        assert all(result.success for result in results)

    def test_context_manager(self):
        """Test client as context manager"""
        with BeemSMSClient("api_key", "secret_key") as client:
            assert client.api_key == "api_key"
            assert hasattr(client, "session")
