# IPLocate geolocation client for Python

[![PyPI version](https://badge.fury.io/py/python-iplocate.svg)](https://badge.fury.io/py/python-iplocate)
[![Python Support](https://img.shields.io/pypi/pyversions/python-iplocate.svg)](https://pypi.org/project/python-iplocate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client for the [IPLocate.io](https://iplocate.io) geolocation API. Look up detailed geolocation and threat intelligence data for any IP address:

- **IP geolocation**: IP to country, IP to city, IP to region/state, coordinates, timezone, postal code
- **ASN information**: Internet service provider, network details, routing information  
- **Privacy & threat detection**: VPN, proxy, Tor, hosting provider detection
- **Company information**: Business details associated with IP addresses - company name, domain, type (ISP/hosting/education/government/business)
- **Abuse contact**: Network abuse reporting information
- **Hosting detection**: Cloud provider and hosting service detection using our proprietary hosting detection engine

See what information we can provide for [your IP address](https://iplocate.io/what-is-my-ip).

## Getting started

You can make 1,000 free requests per day with a [free account](https://iplocate.io/signup). For higher plans, check out [API pricing](https://www.iplocate.io/pricing).

### Installation

```bash
pip install python-iplocate
```

### Quick start

#### Synchronous client

```python
from iplocate import IPLocateClient

# Create a client with your API key
# Get your free API key from https://iplocate.io/signup
client = IPLocateClient(api_key="your-api-key")

# Look up an IP address
result = client.lookup("8.8.8.8")

print(f"IP: {result.ip}")
if result.country:
    print(f"Country: {result.country}")
if result.city:
    print(f"City: {result.city}")

# Check privacy flags
print(f"Is VPN: {result.privacy.is_vpn}")
print(f"Is Proxy: {result.privacy.is_proxy}")
```

#### Asynchronous client

```python
import asyncio
from iplocate import AsyncIPLocateClient

async def main():
    async with AsyncIPLocateClient(api_key="your-api-key") as client:
        result = await client.lookup("8.8.8.8")
        print(f"Country: {result.country}")

asyncio.run(main())
```

### Get your own IP address information

```python
# Look up your own IP address (no IP parameter)
result = client.lookup()
print(f"Your IP: {result.ip}")
```

### Get the country for an IP address

```python
result = client.lookup("203.0.113.1")
print(f"Country: {result.country} ({result.country_code})")
```

### Get the currency code for a country by IP address

```python
result = client.lookup("203.0.113.1")
print(f"Currency: {result.currency_code}")
```

### Get the calling code for a country by IP address

```python
result = client.lookup("203.0.113.1")
print(f"Calling code: {result.calling_code}")
```

## Authentication

Get your free API key from [IPLocate.io](https://iplocate.io/signup), and pass it when creating the client:

```python
client = IPLocateClient(api_key="your-api-key")
```

## Examples

### IP address geolocation lookup

```python
from iplocate import IPLocateClient

client = IPLocateClient(api_key="your-api-key")
result = client.lookup("203.0.113.1")

print(f"Country: {result.country} ({result.country_code})")
if result.latitude and result.longitude:
    print(f"Coordinates: {result.latitude:.4f}, {result.longitude:.4f}")
```

### Check for VPN/Proxy Detection

```python
result = client.lookup("192.0.2.1")

if result.privacy.is_vpn:
    print("This IP is using a VPN")

if result.privacy.is_proxy:
    print("This IP is using a proxy")

if result.privacy.is_tor:
    print("This IP is using Tor")
```

### ASN and network information

```python
result = client.lookup("8.8.8.8")

if result.asn:
    print(f"ASN: {result.asn.asn}")
    print(f"ISP: {result.asn.name}")
    print(f"Network: {result.asn.route}")
```

### Using with different IP address types

```python
import ipaddress
from iplocate import IPLocateClient

client = IPLocateClient(api_key="your-api-key")

# String IP
result1 = client.lookup("8.8.8.8")

# ipaddress objects
ipv4 = ipaddress.IPv4Address("8.8.8.8")
result2 = client.lookup(ipv4)

ipv6 = ipaddress.IPv6Address("2001:4860:4860::8888")
result3 = client.lookup(ipv6)
```

### Custom configuration

```python
import httpx
from iplocate import IPLocateClient, AsyncIPLocateClient

# Custom timeout and base URL
client = IPLocateClient(
    api_key="your-api-key",
    timeout=60.0,
    base_url="https://custom-endpoint.com/api"
)

# Custom HTTP client
custom_http_client = httpx.Client(timeout=60.0)
client = IPLocateClient(
    api_key="your-api-key",
    http_client=custom_http_client
)

# Async with custom client
async_http_client = httpx.AsyncClient(timeout=60.0)
async_client = AsyncIPLocateClient(
    api_key="your-api-key", 
    http_client=async_http_client
)
```

### Context managers

```python
# Synchronous
with IPLocateClient(api_key="your-api-key") as client:
    result = client.lookup("8.8.8.8")
    print(result.country)

# Asynchronous
async with AsyncIPLocateClient(api_key="your-api-key") as client:
    result = await client.lookup("8.8.8.8")
    print(result.country)
```

## Response structure

The `LookupResponse` object contains all available data:

```python
@dataclass
class LookupResponse:
    ip: str
    privacy: Privacy
    country: Optional[str] = None
    country_code: Optional[str] = None
    is_eu: bool = False
    city: Optional[str] = None
    continent: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    time_zone: Optional[str] = None
    postal_code: Optional[str] = None
    subdivision: Optional[str] = None
    currency_code: Optional[str] = None
    calling_code: Optional[str] = None
    network: Optional[str] = None
    asn: Optional[ASN] = None
    company: Optional[Company] = None
    hosting: Optional[Hosting] = None
    abuse: Optional[Abuse] = None
```

Fields marked as `Optional` may be `None` if data is not available.

## Error handling

```python
from iplocate import IPLocateClient
from iplocate.exceptions import (
    APIError, 
    RateLimitError, 
    AuthenticationError, 
    InvalidIPError
)

client = IPLocateClient(api_key="your-api-key")

try:
    result = client.lookup("8.8.8.8")
except InvalidIPError as e:
    print(f"Invalid IP address: {e.ip}")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except APIError as e:
    print(f"API error ({e.status_code}): {e.message}")
```

Common API errors:

- `InvalidIPError`: Invalid IP address format
- `AuthenticationError`: Invalid API key (HTTP 403)
- `NotFoundError`: IP address not found (HTTP 404)
- `RateLimitError`: Rate limit exceeded (HTTP 429)
- `APIError`: Other API errors (HTTP 500, etc.)

## Async/await support

The library provides full async support with `AsyncIPLocateClient`:

```python
import asyncio
from iplocate import AsyncIPLocateClient

async def lookup_multiple_ips():
    async with AsyncIPLocateClient(api_key="your-api-key") as client:
        # Concurrent lookups
        tasks = [
            client.lookup("8.8.8.8"),
            client.lookup("1.1.1.1"),
            client.lookup("208.67.222.222")
        ]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"{result.ip}: {result.country}")

asyncio.run(lookup_multiple_ips())
```

## API reference

For complete API documentation, visit [iplocate.io/docs](https://iplocate.io/docs).

## Requirements

- Python 3.8+
- httpx >= 0.24.0

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run type checking:

```bash
mypy iplocate
```

Format code:

```bash
black iplocate tests
isort iplocate tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## About IPLocate.io

Since 2017, IPLocate has set out to provide the most reliable and accurate IP address data.

We process 50TB+ of data to produce our comprehensive IP geolocation, IP to company, proxy and VPN detection, hosting detection, ASN, and WHOIS data sets. Our API handles over 15 billion requests a month for thousands of businesses and developers.

- Email: [support@iplocate.io](mailto:support@iplocate.io)
- Website: [iplocate.io](https://iplocate.io)
- Documentation: [iplocate.io/docs](https://iplocate.io/docs)
- Sign up for a free API Key: [iplocate.io/signup](https://iplocate.io/signup)
