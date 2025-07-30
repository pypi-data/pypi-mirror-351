"""Tests for the IPLocate data models."""

import pytest

from iplocate.models import ASN, Abuse, Company, Hosting, LookupResponse, Privacy


class TestModels:
    """Tests for IPLocate data models."""

    def test_asn_creation(self):
        asn = ASN(
            asn="AS15169",
            route="8.8.8.0/24",
            netname="GOOGLE",
            name="Google LLC",
            country_code="US",
            domain="google.com",
            type="content",
            rir="ARIN",
        )
        assert asn.asn == "AS15169"
        assert asn.name == "Google LLC"
        assert asn.domain == "google.com"

    def test_privacy_creation(self):
        privacy = Privacy(
            is_abuser=False,
            is_anonymous=False,
            is_bogon=False,
            is_hosting=False,
            is_icloud_relay=False,
            is_proxy=False,
            is_tor=False,
            is_vpn=True,
        )
        assert privacy.is_vpn is True
        assert privacy.is_proxy is False
        assert privacy.is_tor is False

    def test_company_creation(self):
        company = Company(
            name="Google LLC", domain="google.com", country_code="US", type="content"
        )
        assert company.name == "Google LLC"
        assert company.domain == "google.com"
        assert company.country_code == "US"

    def test_hosting_creation_with_defaults(self):
        hosting = Hosting()
        assert hosting.provider is None
        assert hosting.domain is None
        assert hosting.network is None
        assert hosting.region is None
        assert hosting.service is None

    def test_hosting_creation_with_values(self):
        hosting = Hosting(
            provider="Amazon Web Services",
            domain="aws.amazon.com",
            network="52.95.0.0/16",
            region="us-east-1",
            service="EC2",
        )
        assert hosting.provider == "Amazon Web Services"
        assert hosting.service == "EC2"

    def test_abuse_creation_with_defaults(self):
        abuse = Abuse()
        assert abuse.address is None
        assert abuse.email is None
        assert abuse.name is None

    def test_abuse_creation_with_values(self):
        abuse = Abuse(
            address="1600 Amphitheatre Parkway",
            country_code="US",
            email="abuse@google.com",
            name="Google LLC",
            network="8.8.8.0/24",
            phone="+1-650-253-0000",
        )
        assert abuse.email == "abuse@google.com"
        assert abuse.phone == "+1-650-253-0000"

    def test_lookup_response_minimal(self):
        privacy = Privacy(
            is_abuser=False,
            is_anonymous=False,
            is_bogon=False,
            is_hosting=False,
            is_icloud_relay=False,
            is_proxy=False,
            is_tor=False,
            is_vpn=False,
        )

        response = LookupResponse(ip="8.8.8.8", privacy=privacy)

        assert response.ip == "8.8.8.8"
        assert response.country is None
        assert response.city is None
        assert response.asn is None
        assert response.privacy.is_vpn is False

    def test_lookup_response_complete(self):
        asn = ASN(
            asn="AS15169",
            route="8.8.8.0/24",
            netname="GOOGLE",
            name="Google LLC",
            country_code="US",
            domain="google.com",
            type="content",
            rir="ARIN",
        )

        privacy = Privacy(
            is_abuser=False,
            is_anonymous=False,
            is_bogon=False,
            is_hosting=False,
            is_icloud_relay=False,
            is_proxy=False,
            is_tor=False,
            is_vpn=False,
        )

        company = Company(
            name="Google LLC", domain="google.com", country_code="US", type="content"
        )

        response = LookupResponse(
            ip="8.8.8.8",
            country="United States",
            country_code="US",
            is_eu=False,
            city="Mountain View",
            continent="North America",
            latitude=37.4056,
            longitude=-122.0775,
            time_zone="America/Los_Angeles",
            postal_code="94043",
            subdivision="California",
            currency_code="USD",
            calling_code="+1",
            network="8.8.8.0/24",
            asn=asn,
            privacy=privacy,
            company=company,
        )

        assert response.ip == "8.8.8.8"
        assert response.country == "United States"
        assert response.city == "Mountain View"
        assert response.latitude == 37.4056
        assert response.asn.name == "Google LLC"
        assert response.privacy.is_vpn is False
        assert response.company.domain == "google.com"
