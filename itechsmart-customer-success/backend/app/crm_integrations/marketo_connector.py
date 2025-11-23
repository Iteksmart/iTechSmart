"""
Marketo CRM Connector
Integration with Adobe Marketo Engage
"""

import aiohttp
import asyncio
import hashlib
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging
from urllib.parse import urlencode

from .base_crm import (
    BaseCRMConnector,
    CRMContact,
    CRMOpportunity,
    CRMAccount,
    AuthenticationError,
)


class MarketoConnector(BaseCRMConnector):
    """Marketo CRM connector using REST API"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = f"{config['endpoint']}/rest"
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.session = None
        self.token_expiry = None

    async def authenticate(self) -> bool:
        """Authenticate using OAuth 2.0 client credentials flow"""
        try:
            auth_url = f"{self.base_url}/identity/oauth/token"

            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(auth_url, params=auth_data) as response:
                    if response.status == 200:
                        auth_result = await response.json()
                        self.access_token = auth_result["access_token"]
                        self.token_expiry = (
                            time.time() + auth_result["expires_in"] - 60
                        )  # Buffer
                        self.session = aiohttp.ClientSession(
                            headers={"Authorization": f"Bearer {self.access_token}"}
                        )
                        return True
                    else:
                        error_data = await response.json()
                        raise AuthenticationError(f"Marketo auth failed: {error_data}")

        except Exception as e:
            self.logger.error(f"Marketo authentication error: {str(e)}")
            return False

    async def _ensure_auth(self):
        """Ensure we have a valid token"""
        if not self.access_token or (
            self.token_expiry and time.time() > self.token_expiry
        ):
            await self.authenticate()

    async def get_contacts(self, limit: int = 100, offset: int = 0) -> List[CRMContact]:
        """Retrieve leads using Marketo API"""
        await self._ensure_auth()
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/v1/leads.json"
        params = {
            "batchSize": min(limit, 300),  # Marketo max is 300
            "nextPageToken": str(offset) if offset else None,
        }
        params = {k: v for k, v in params.items() if v is not None}

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return [
                    self._convert_contact(record) for record in data.get("result", [])
                ]
            else:
                error_data = await response.text()
                raise Exception(
                    f"Failed to get contacts: {response.status} - {error_data}"
                )

    async def get_contact(self, contact_id: str) -> Optional[CRMContact]:
        """Retrieve specific lead by ID"""
        await self._ensure_auth()
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/v1/lead/{contact_id}.json"

        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                records = data.get("result", [])
                return self._convert_contact(records[0]) if records else None
            elif response.status == 404:
                return None
            else:
                raise Exception(f"Failed to get contact: {response.status}")

    async def update_contact(self, contact_id: str, data: Dict[str, Any]) -> bool:
        """Update lead record"""
        await self._ensure_auth()
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/v1/leads.json"
        payload = {
            "action": "updateOnly",
            "lookupField": "id",
            "input": [{"id": contact_id, **data}],
        }

        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("success", False)
            else:
                raise Exception(f"Failed to update contact: {response.status}")

    async def create_contact(self, contact: CRMContact) -> str:
        """Create new lead"""
        await self._ensure_auth()
        if not self.session:
            raise AuthenticationError("Not authenticated")

        lead_data = {
            "email": contact.email,
            "firstName": contact.first_name,
            "lastName": contact.last_name,
        }

        if contact.phone:
            lead_data["phone"] = contact.phone
        if contact.company:
            lead_data["company"] = contact.company
        if contact.title:
            lead_data["title"] = contact.title
        if contact.source:
            lead_data["leadSource"] = contact.source

        url = f"{self.base_url}/v1/leads.json"
        payload = {"action": "createOnly", "input": [lead_data]}

        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                records = result.get("result", [])
                return str(records[0]["id"]) if records else None
            else:
                error_data = await response.text()
                raise Exception(
                    f"Failed to create contact: {response.status} - {error_data}"
                )

    async def get_opportunities(
        self, contact_id: Optional[str] = None
    ) -> List[CRMOpportunity]:
        """Retrieve opportunities"""
        await self._ensure_auth()
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/v1/opportunities.json"
        params = {"batchSize": 300}

        if contact_id:
            # Filter by lead ID
            params["filterType"] = "leadId"
            params["filterValues"] = contact_id

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return [
                    self._convert_opportunity(record)
                    for record in data.get("result", [])
                ]
            else:
                raise Exception(f"Failed to get opportunities: {response.status}")

    async def get_accounts(self) -> List[CRMAccount]:
        """Retrieve companies"""
        await self._ensure_auth()
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/v1/companies.json"
        params = {"batchSize": 300}

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return [
                    self._convert_account(record) for record in data.get("result", [])
                ]
            else:
                raise Exception(f"Failed to get companies: {response.status}")

    def _convert_contact(self, record: Dict[str, Any]) -> CRMContact:
        """Convert Marketo lead to standard format"""
        return CRMContact(
            id=str(record.get("id", "")),
            email=record.get("email", ""),
            first_name=record.get("firstName", ""),
            last_name=record.get("lastName", ""),
            phone=record.get("phone"),
            company=record.get("company"),
            title=record.get("title"),
            lead_score=record.get("leadScore"),
            source=record.get("leadSource"),
            created_date=self._parse_date(record.get("createdAt")),
            last_updated=self._parse_date(record.get("updatedAt")),
        )

    def _convert_opportunity(self, record: Dict[str, Any]) -> CRMOpportunity:
        """Convert Marketo opportunity to standard format"""
        return CRMOpportunity(
            id=str(record.get("id", "")),
            contact_id=str(record.get("leadId", "")) if record.get("leadId") else None,
            name=record.get("name", ""),
            stage=record.get("stage", ""),
            value=record.get("amount"),
            probability=record.get("probability"),
            close_date=self._parse_date(record.get("closeDate")),
            created_date=self._parse_date(record.get("createdAt")),
        )

    def _convert_account(self, record: Dict[str, Any]) -> CRMAccount:
        """Convert Marketo company to standard format"""
        address = None
        if any(
            [
                record.get("billingCity"),
                record.get("billingState"),
                record.get("billingCountry"),
            ]
        ):
            address = {
                "city": record.get("billingCity"),
                "state": record.get("billingState"),
                "country": record.get("billingCountry"),
            }

        return CRMAccount(
            id=str(record.get("id", "")),
            name=record.get("name", ""),
            industry=record.get("industry"),
            size=record.get("companySize"),
            revenue=record.get("annualRevenue"),
            website=record.get("website"),
            phone=record.get("phone"),
            address=address,
            created_date=self._parse_date(record.get("createdAt")),
        )

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Marketo datetime string"""
        if not date_str:
            return None
        try:
            # Marketo uses ISO format
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            return None

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
