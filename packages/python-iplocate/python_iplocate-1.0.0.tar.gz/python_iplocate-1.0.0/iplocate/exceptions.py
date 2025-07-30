"""Custom exceptions for the IPLocate client."""


class IPLocateError(Exception):
    """Base exception for all IPLocate client errors."""

    pass


class APIError(IPLocateError):
    """Exception raised for API errors from the IPLocate service."""

    def __init__(self, message: str, status_code: int, response_text: str = ""):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        return f"IPLocate API error ({self.status_code}): {self.message}"


class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded (HTTP 429)."""

    def __init__(self, message: str = "Rate limit exceeded", response_text: str = ""):
        super().__init__(message, 429, response_text)


class AuthenticationError(APIError):
    """Exception raised for authentication errors (HTTP 403)."""

    def __init__(self, message: str = "Invalid API key", response_text: str = ""):
        super().__init__(message, 403, response_text)


class InvalidIPError(IPLocateError):
    """Exception raised when an invalid IP address is provided."""

    def __init__(self, ip: str):
        self.ip = ip
        super().__init__(f"Invalid IP address: {ip}")


class NotFoundError(APIError):
    """Exception raised when IP address is not found (HTTP 404)."""

    def __init__(self, message: str = "IP address not found", response_text: str = ""):
        super().__init__(message, 404, response_text)
