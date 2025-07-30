"""Tests for IPLocate exceptions."""

import pytest

from iplocate.exceptions import (
    APIError,
    AuthenticationError,
    InvalidIPError,
    IPLocateError,
    NotFoundError,
    RateLimitError,
)


class TestExceptions:
    """Tests for IPLocate custom exceptions."""

    def test_iplocate_error_base(self):
        error = IPLocateError("Base error")
        assert str(error) == "Base error"
        assert isinstance(error, Exception)

    def test_api_error(self):
        error = APIError("API error message", 400, "response body")
        assert error.message == "API error message"
        assert error.status_code == 400
        assert error.response_text == "response body"
        assert str(error) == "IPLocate API error (400): API error message"

    def test_api_error_inheritance(self):
        error = APIError("API error", 500)
        assert isinstance(error, IPLocateError)
        assert isinstance(error, Exception)

    def test_rate_limit_error(self):
        error = RateLimitError()
        assert error.status_code == 429
        assert error.message == "Rate limit exceeded"
        assert str(error) == "IPLocate API error (429): Rate limit exceeded"

    def test_rate_limit_error_custom_message(self):
        error = RateLimitError("Custom rate limit message", "response")
        assert error.message == "Custom rate limit message"
        assert error.response_text == "response"
        assert error.status_code == 429

    def test_authentication_error(self):
        error = AuthenticationError()
        assert error.status_code == 403
        assert error.message == "Invalid API key"
        assert str(error) == "IPLocate API error (403): Invalid API key"

    def test_authentication_error_custom(self):
        error = AuthenticationError("Custom auth error", "body")
        assert error.message == "Custom auth error"
        assert error.response_text == "body"

    def test_invalid_ip_error(self):
        error = InvalidIPError("not-an-ip")
        assert error.ip == "not-an-ip"
        assert str(error) == "Invalid IP address: not-an-ip"
        assert isinstance(error, IPLocateError)

    def test_not_found_error(self):
        error = NotFoundError()
        assert error.status_code == 404
        assert error.message == "IP address not found"
        assert str(error) == "IPLocate API error (404): IP address not found"

    def test_not_found_error_custom(self):
        error = NotFoundError("Custom not found", "response")
        assert error.message == "Custom not found"
        assert error.response_text == "response"
        assert error.status_code == 404

    def test_exception_hierarchy(self):
        """Test that all exceptions inherit correctly."""
        # All API errors should inherit from APIError
        assert issubclass(RateLimitError, APIError)
        assert issubclass(AuthenticationError, APIError)
        assert issubclass(NotFoundError, APIError)

        # All errors should inherit from IPLocateError
        assert issubclass(APIError, IPLocateError)
        assert issubclass(InvalidIPError, IPLocateError)

        # All should ultimately inherit from Exception
        assert issubclass(IPLocateError, Exception)
