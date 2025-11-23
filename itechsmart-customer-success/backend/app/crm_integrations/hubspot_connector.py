"""
HubSpot CRM Connector
Integration with HubSpot CRM Hub
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging

from .base_crm import (
    BaseCRMConnector,
    CRMContact,
    CRMOpportunity,
    CRMAccount,
    AuthenticationError,
)


class HubSpotConnector(BaseCRMConnector):
    """HubSpot CRM connector using REST API"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.hubapi.com"
        self.api_version = config.get("api_version", "v3")
        self.session = None

    async def authenticate(self) -> bool:
        """Authenticate using private app access token"""
        try:
            if "access_token" not in self.config:
                raise AuthenticationError("HubSpot access token is required")

            self.access_token = self.config["access_token"]
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

            # Test authentication by making a simple request
            test_url = f"{self.base_url}/crm/v3/objects/contacts?limit=1"
            async with self.session.get(test_url) as response:
                return response.status == 200

        except Exception as e:
            self.logger.error(f"HubSpot authentication error: {str(e)}")
            return False

    async def get_contacts(self, limit: int = 100, offset: int = 0) -> List[CRMContact]:
        """Retrieve contacts using HubSpot API"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/crm/{self.api_version}/objects/contacts"
        params = {"limit": min(limit, 100), "after": offset}  # HubSpot max limit is 100

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return [
                    self._convert_contact(record) for record in data.get("results", [])
                ]
            else:
                error_data = await response.text()
                raise Exception(
                    f"Failed to get contacts: {response.status} - {error_data}"
                )

    async def get_contact(self, contact_id: str) -> Optional[CRMContact]:
        """Retrieve specific contact by ID"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/crm/{self.api_version}/objects/contacts/{contact_id}"

        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return self._convert_contact(data)
            elif response.status == 404:
                return None
            else:
                raise Exception(f"Failed to get contact: {response.status}")

    async def update_contact(self, contact_id: str, data: Dict[str, Any]) -> bool:
        """Update contact record"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/crm/{self.api_version}/objects/contacts/{contact_id}"
        payload = {"properties": data}

        async with self.session.patch(url, json=payload) as response:
            return response.status == 200

    async def create_contact(self, contact: CRMContact) -> str:
        """Create new contact"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        properties = {
            "email": contact.email,
            "firstname": contact.first_name,
            "lastname": contact.last_name,
        }

        if contact.phone:
            properties["phone"] = contact.phone
        if contact.company:
            properties["company"] = contact.company
        if contact.title:
            properties["jobtitle"] = contact.title
        if contact.lead_score:
            properties["hs_lead_score"] = str(contact.lead_score)
        if contact.source:
            properties["lifecyclestage"] = contact.source

        payload = {"properties": properties}
        url = f"{self.base_url}/crm/{self.api_version}/objects/contacts"

        async with self.session.post(url, json=payload) as response:
            if response.status == 201:
                result = await response.json()
                return result["id"]
            else:
                error_data = await response.text()
                raise Exception(
                    f"Failed to create contact: {response.status} - {error_data}"
                )

    async def get_opportunities(
        self, contact_id: Optional[str] = None
    ) -> List[CRMOpportunity]:
        """Retrieve deals (opportunities)"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/crm/{self.api_version}/objects/deals"
        params = {"limit": 100}

        if contact_id:
            # Filter by contact association
            params["associations"] = "contacts"

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                deals = data.get("results", [])
                return [self._convert_opportunity(deal) for deal in deals]
            else:
                raise Exception(f"Failed to get deals: {response.status}")

    async def get_accounts(self) -> List[CRMAccount]:
        """Retrieve companies (accounts)"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/crm/{self.api_version}/objects/companies"
        params = {"limit": 100}

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return [
                    self._convert_account(record) for record in data.get("results", [])
                ]
            else:
                raise Exception(f"Failed to get companies: {response.status}")

    def _convert_contact(self, record: Dict[str, Any]) -> CRMContact:
        """Convert HubSpot contact to standard format"""
        properties = record.get("properties", {})
        created_at = properties.get("createdate")
        updated_at = properties.get("lastmodifieddate")

        return CRMContact(
            id=record["id"],
            email=properties.get("email", ""),
            first_name=properties.get("firstname", ""),
            last_name=properties.get("lastname", ""),
            phone=properties.get("phone"),
            company=properties.get("company"),
            title=properties.get("jobtitle"),
            lead_score=(
                int(properties.get("hs_lead_score", 0))
                if properties.get("hs_lead_score")
                else None
            ),
            source=properties.get("lifecyclestage"),
            created_date=self._parse_date(created_at),
            last_updated=self._parse_date(updated_at),
        )

    def _convert_opportunity(self, record: Dict[str, Any]) -> CRMOpportunity:
        """Convert HubSpot deal to standard format"""
        properties = record.get("properties", {})

        return CRMOpportunity(
            id=record["id"],
            contact_id=None,  # Would need to query associations
            name=properties.get("dealname", ""),
            stage=properties.get("dealstage", ""),
            value=(
                float(properties.get("amount", 0)) if properties.get("amount") else None
            ),
            probability=None,  # HubSpot doesn't have probability by default
            close_date=self._parse_date(properties.get("closedate")),
            created_date=self._parse_date(properties.get("createdate")),
        )

    def _convert_account(self, record: Dict[str, Any]) -> CRMAccount:
        """Convert HubSpot company to standard format"""
        properties = record.get("properties", {})

        address = None
        if any(
            [properties.get("city"), properties.get("state"), properties.get("country")]
        ):
            address = {
                "city": properties.get("city"),
                "state": properties.get("state"),
                "country": properties.get("country"),
            }

        return CRMAccount(
            id=record["id"],
            name=properties.get("name", ""),
            industry=properties.get("industry"),
            size=properties.get("type"),
            revenue=(
                float(properties.get("annualrevenue", 0))
                if properties.get("annualrevenue")
                else None
            ),
            website=properties.get("website"),
            phone=properties.get("phone"),
            address=address,
            created_date=self._parse_date(properties.get("createdate")),
        )

    def _parse_date(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse HubSpot timestamp (milliseconds since epoch)"""
        if not timestamp_str:
            return None
        try:
            # HubSpot uses milliseconds since epoch
            timestamp = int(timestamp_str)
            return datetime.fromtimestamp(timestamp / 1000)
        except:
            return None

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
