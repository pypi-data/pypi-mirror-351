"""Synchronous and asynchronous clients for the IPLocate API."""

from __future__ import annotations

import ipaddress
import sys
from typing import Optional, Union
from urllib.parse import urlencode, urljoin

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    InvalidIPError,
    NotFoundError,
    RateLimitError,
)
from .models import ASN, Abuse, Company, Hosting, LookupResponse, Privacy

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

# Type aliases
IPAddress: TypeAlias = Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address]

DEFAULT_BASE_URL = "https://iplocate.io/api"
DEFAULT_TIMEOUT = 30.0


class BaseClient:
    """Base client with shared functionality."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the client.

        Args:
            api_key: Your IPLocate API key (get one free at iplocate.io/signup)
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _validate_ip(self, ip: str) -> str:
        """Validate IP address format."""
        try:
            # This will raise ValueError for invalid IPs
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            raise InvalidIPError(ip)

    def _build_url(self, ip: Optional[str] = None) -> str:
        """Build the API URL with optional IP and API key."""
        if ip is None:
            url = f"{self.base_url}/lookup/"
        else:
            validated_ip = self._validate_ip(ip)
            url = f"{self.base_url}/lookup/{validated_ip}"

        if self.api_key:
            query_params = urlencode({"apikey": self.api_key})
            url += f"?{query_params}"

        return url

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle HTTP error responses."""
        try:
            error_data = response.json()
            error_message = error_data.get("error", f"HTTP {response.status_code}")
        except Exception:
            error_message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 400:
            raise InvalidIPError(error_message)
        elif response.status_code == 403:
            raise AuthenticationError(error_message, response.text)
        elif response.status_code == 404:
            raise NotFoundError(error_message, response.text)
        elif response.status_code == 429:
            raise RateLimitError(error_message, response.text)
        else:
            raise APIError(error_message, response.status_code, response.text)

    def _parse_response(self, data: dict) -> LookupResponse:
        """Parse API response data into LookupResponse object."""
        # Parse nested objects
        asn_data = data.get("asn")
        asn = ASN(**asn_data) if asn_data else None

        privacy_data = data.get("privacy", {})
        privacy = Privacy(**privacy_data)

        company_data = data.get("company")
        company = Company(**company_data) if company_data else None

        hosting_data = data.get("hosting")
        hosting = Hosting(**hosting_data) if hosting_data else None

        abuse_data = data.get("abuse")
        abuse = Abuse(**abuse_data) if abuse_data else None

        return LookupResponse(
            ip=data["ip"],
            country=data.get("country"),
            country_code=data.get("country_code"),
            is_eu=data.get("is_eu", False),
            city=data.get("city"),
            continent=data.get("continent"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            time_zone=data.get("time_zone"),
            postal_code=data.get("postal_code"),
            subdivision=data.get("subdivision"),
            currency_code=data.get("currency_code"),
            calling_code=data.get("calling_code"),
            network=data.get("network"),
            asn=asn,
            privacy=privacy,
            company=company,
            hosting=hosting,
            abuse=abuse,
        )


class IPLocateClient(BaseClient):
    """Synchronous client for the IPLocate API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: Optional[httpx.Client] = None,
    ):
        """
        Initialize the synchronous client.

        Args:
            api_key: Your IPLocate API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            http_client: Custom httpx.Client instance
        """
        super().__init__(api_key, base_url, timeout)
        self._client = http_client or httpx.Client(
            timeout=timeout,
            headers={
                "User-Agent": "python-iplocate/1.0.0",
                "Accept": "application/json",
            },
        )
        self._should_close_client = http_client is None

    def __enter__(self) -> IPLocateClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        if self._should_close_client:
            self._client.close()

    def lookup(self, ip: Optional[IPAddress] = None) -> LookupResponse:
        """
        Look up geolocation and threat intelligence data for an IP address.

        Args:
            ip: IP address to look up. If None, looks up the client's own IP.

        Returns:
            LookupResponse containing all available data

        Raises:
            InvalidIPError: Invalid IP address format
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            NotFoundError: IP address not found
            APIError: Other API errors
        """
        ip_str = str(ip) if ip is not None else None
        url = self._build_url(ip_str)

        response = self._client.get(url)

        if not response.is_success:
            self._handle_error_response(response)

        return self._parse_response(response.json())


class AsyncIPLocateClient(BaseClient):
    """Asynchronous client for the IPLocate API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        """
        Initialize the asynchronous client.

        Args:
            api_key: Your IPLocate API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            http_client: Custom httpx.AsyncClient instance
        """
        super().__init__(api_key, base_url, timeout)
        self._client = http_client or httpx.AsyncClient(
            timeout=timeout,
            headers={
                "User-Agent": "python-iplocate/1.0.0",
                "Accept": "application/json",
            },
        )
        self._should_close_client = http_client is None

    async def __aenter__(self) -> AsyncIPLocateClient:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._should_close_client:
            await self._client.aclose()

    async def lookup(self, ip: Optional[IPAddress] = None) -> LookupResponse:
        """
        Look up geolocation and threat intelligence data for an IP address.

        Args:
            ip: IP address to look up. If None, looks up the client's own IP.

        Returns:
            LookupResponse containing all available data

        Raises:
            InvalidIPError: Invalid IP address format
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            NotFoundError: IP address not found
            APIError: Other API errors
        """
        ip_str = str(ip) if ip is not None else None
        url = self._build_url(ip_str)

        response = await self._client.get(url)

        if not response.is_success:
            self._handle_error_response(response)

        return self._parse_response(response.json())
