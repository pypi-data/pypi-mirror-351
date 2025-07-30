"""Tests for the IPLocate client."""

import ipaddress
import json
from unittest.mock import Mock, patch

import httpx
import pytest

from iplocate import AsyncIPLocateClient, IPLocateClient
from iplocate.exceptions import (
    APIError,
    AuthenticationError,
    InvalidIPError,
    NotFoundError,
    RateLimitError,
)
from iplocate.models import LookupResponse, Privacy


class TestIPLocateClient:
    """Tests for the synchronous IPLocate client."""

    def test_init_default(self):
        client = IPLocateClient()
        assert client.api_key is None
        assert client.base_url == "https://iplocate.io/api"
        assert client.timeout == 30.0

    def test_init_with_params(self):
        client = IPLocateClient(
            api_key="test-key", base_url="https://custom.api.com", timeout=60.0
        )
        assert client.api_key == "test-key"
        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60.0

    def test_context_manager(self):
        with IPLocateClient() as client:
            assert isinstance(client, IPLocateClient)

    def test_validate_ip_valid(self):
        client = IPLocateClient()
        assert client._validate_ip("8.8.8.8") == "8.8.8.8"
        assert client._validate_ip("2001:4860:4860::8888") == "2001:4860:4860::8888"

    def test_validate_ip_invalid(self):
        client = IPLocateClient()
        with pytest.raises(InvalidIPError):
            client._validate_ip("invalid-ip")

    def test_build_url_without_ip(self):
        client = IPLocateClient()
        url = client._build_url()
        assert url == "https://iplocate.io/api/lookup/"

    def test_build_url_with_ip(self):
        client = IPLocateClient()
        url = client._build_url("8.8.8.8")
        assert url == "https://iplocate.io/api/lookup/8.8.8.8"

    def test_build_url_with_api_key(self):
        client = IPLocateClient(api_key="test-key")
        url = client._build_url("8.8.8.8")
        assert url == "https://iplocate.io/api/lookup/8.8.8.8?apikey=test-key"

    @pytest.fixture
    def mock_response_data(self):
        return {
            "ip": "8.8.8.8",
            "country": "United States",
            "country_code": "US",
            "is_eu": False,
            "city": "Mountain View",
            "continent": "North America",
            "latitude": 37.4056,
            "longitude": -122.0775,
            "time_zone": "America/Los_Angeles",
            "postal_code": "94043",
            "subdivision": "California",
            "currency_code": "USD",
            "calling_code": "+1",
            "network": "8.8.8.0/24",
            "asn": {
                "asn": "AS15169",
                "route": "8.8.8.0/24",
                "netname": "GOOGLE",
                "name": "Google LLC",
                "country_code": "US",
                "domain": "google.com",
                "type": "content",
                "rir": "ARIN",
            },
            "privacy": {
                "is_abuser": False,
                "is_anonymous": False,
                "is_bogon": False,
                "is_hosting": False,
                "is_icloud_relay": False,
                "is_proxy": False,
                "is_tor": False,
                "is_vpn": False,
            },
            "company": {
                "name": "Google LLC",
                "domain": "google.com",
                "country_code": "US",
                "type": "content",
            },
            "hosting": None,
            "abuse": {
                "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",
                "country_code": "US",
                "email": "network-abuse@google.com",
                "name": "Google LLC",
                "network": "8.8.8.0/24",
                "phone": "+1-650-253-0000",
            },
        }

    def test_parse_response(self, mock_response_data):
        client = IPLocateClient()
        result = client._parse_response(mock_response_data)

        assert isinstance(result, LookupResponse)
        assert result.ip == "8.8.8.8"
        assert result.country == "United States"
        assert result.city == "Mountain View"
        assert result.asn.name == "Google LLC"
        assert result.privacy.is_vpn is False
        assert result.company.domain == "google.com"

    @patch("httpx.Client.get")
    def test_lookup_success(self, mock_get, mock_response_data):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = mock_response_data
        mock_get.return_value = mock_response

        client = IPLocateClient(api_key="test-key")
        result = client.lookup("8.8.8.8")

        assert isinstance(result, LookupResponse)
        assert result.ip == "8.8.8.8"
        mock_get.assert_called_once()

    @patch("httpx.Client.get")
    def test_lookup_invalid_ip(self, mock_get):
        client = IPLocateClient()
        with pytest.raises(InvalidIPError):
            client.lookup("invalid-ip")

        mock_get.assert_not_called()

    @patch("httpx.Client.get")
    def test_lookup_rate_limit_error(self, mock_get):
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.text = '{"error": "Rate limit exceeded"}'
        mock_get.return_value = mock_response

        client = IPLocateClient()
        with pytest.raises(RateLimitError):
            client.lookup("8.8.8.8")

    @patch("httpx.Client.get")
    def test_lookup_auth_error(self, mock_get):
        mock_response = Mock()
        mock_response.is_success = False
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_response.text = '{"error": "Invalid API key"}'
        mock_get.return_value = mock_response

        client = IPLocateClient()
        with pytest.raises(AuthenticationError):
            client.lookup("8.8.8.8")

    def test_lookup_with_ipaddress_object(self):
        with patch("httpx.Client.get") as mock_get:
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.json.return_value = {
                "ip": "8.8.8.8",
                "privacy": {
                    "is_vpn": False,
                    "is_proxy": False,
                    "is_tor": False,
                    "is_abuser": False,
                    "is_anonymous": False,
                    "is_bogon": False,
                    "is_hosting": False,
                    "is_icloud_relay": False,
                },
            }
            mock_get.return_value = mock_response

            client = IPLocateClient()
            ip_obj = ipaddress.ip_address("8.8.8.8")
            result = client.lookup(ip_obj)

            assert result.ip == "8.8.8.8"


class TestAsyncIPLocateClient:
    """Tests for the asynchronous IPLocate client."""

    def test_init_default(self):
        client = AsyncIPLocateClient()
        assert client.api_key is None
        assert client.base_url == "https://iplocate.io/api"
        assert client.timeout == 30.0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        async with AsyncIPLocateClient() as client:
            assert isinstance(client, AsyncIPLocateClient)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_lookup_success(self, mock_get):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "ip": "8.8.8.8",
            "country": "United States",
            "privacy": {
                "is_vpn": False,
                "is_proxy": False,
                "is_tor": False,
                "is_abuser": False,
                "is_anonymous": False,
                "is_bogon": False,
                "is_hosting": False,
                "is_icloud_relay": False,
            },
        }
        mock_get.return_value = mock_response

        client = AsyncIPLocateClient(api_key="test-key")
        result = await client.lookup("8.8.8.8")

        assert isinstance(result, LookupResponse)
        assert result.ip == "8.8.8.8"
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_lookup_invalid_ip(self):
        client = AsyncIPLocateClient()
        with pytest.raises(InvalidIPError):
            await client.lookup("invalid-ip")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.get")
    async def test_lookup_self(self, mock_get):
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "ip": "203.0.113.1",
            "privacy": {
                "is_vpn": False,
                "is_proxy": False,
                "is_tor": False,
                "is_abuser": False,
                "is_anonymous": False,
                "is_bogon": False,
                "is_hosting": False,
                "is_icloud_relay": False,
            },
        }
        mock_get.return_value = mock_response

        client = AsyncIPLocateClient()
        result = await client.lookup()  # No IP provided = self lookup

        assert isinstance(result, LookupResponse)
        assert result.ip == "203.0.113.1"
