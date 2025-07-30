"""Data models for IPLocate API responses."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


@dataclass
class ASN:
    """Autonomous System Number information."""

    asn: str
    route: str
    netname: str
    name: str
    country_code: str
    domain: str
    type: str
    rir: str


@dataclass
class Privacy:
    """Privacy and threat detection information."""

    is_abuser: bool
    is_anonymous: bool
    is_bogon: bool
    is_hosting: bool
    is_icloud_relay: bool
    is_proxy: bool
    is_tor: bool
    is_vpn: bool


@dataclass
class Company:
    """Company information associated with the IP address."""

    name: str
    domain: str
    country_code: str
    type: str


@dataclass
class Hosting:
    """Hosting provider information."""

    provider: Optional[str] = None
    domain: Optional[str] = None
    network: Optional[str] = None
    region: Optional[str] = None
    service: Optional[str] = None


@dataclass
class Abuse:
    """Abuse contact information."""

    address: Optional[str] = None
    country_code: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    network: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class LookupResponse:
    """Complete response from the IPLocate API."""

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


# Type alias for convenience
IPLookupResult: TypeAlias = LookupResponse
