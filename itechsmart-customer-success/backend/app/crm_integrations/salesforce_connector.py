"""
Salesforce CRM Connector
Integration with Salesforce Sales Cloud and Service Cloud
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


class SalesforceConnector(BaseCRMConnector):
    """Salesforce CRM connector using REST API"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = None
        self.api_version = config.get("api_version", "56.0")
        self.session = None

    async def authenticate(self) -> bool:
        """Authenticate using OAuth 2.0 flow"""
        try:
            auth_url = f"https://login.salesforce.com/services/oauth2/token"

            auth_data = {
                "grant_type": "password",
                "client_id": self.config["client_id"],
                "client_secret": self.config["client_secret"],
                "username": self.config["username"],
                "password": self.config["password"],
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, data=auth_data) as response:
                    if response.status == 200:
                        auth_result = await response.json()
                        self.access_token = auth_result["access_token"]
                        self.base_url = auth_result["instance_url"]
                        self.session = aiohttp.ClientSession(
                            headers={"Authorization": f"Bearer {self.access_token}"}
                        )
                        return True
                    else:
                        error_data = await response.json()
                        raise AuthenticationError(
                            f"Salesforce auth failed: {error_data}"
                        )

        except Exception as e:
            self.logger.error(f"Salesforce authentication error: {str(e)}")
            return False

    async def get_contacts(self, limit: int = 100, offset: int = 0) -> List[CRMContact]:
        """Retrieve contacts using SOQL query"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        soql_query = f"""
            SELECT Id, Email, FirstName, LastName, Phone, Company, Title, 
                   LeadSource, CreatedDate, LastModifiedDate, LeadScore
            FROM Contact 
            LIMIT {limit} OFFSET {offset}
        """

        url = f"{self.base_url}/services/data/v{self.api_version}/query/"
        params = {"q": soql_query}

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return [
                    self._convert_contact(record) for record in data.get("records", [])
                ]
            else:
                raise Exception(f"Failed to get contacts: {response.status}")

    async def get_contact(self, contact_id: str) -> Optional[CRMContact]:
        """Retrieve specific contact by ID"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        soql_query = f"""
            SELECT Id, Email, FirstName, LastName, Phone, Company, Title, 
                   LeadSource, CreatedDate, LastModifiedDate, LeadScore
            FROM Contact 
            WHERE Id = '{contact_id}'
        """

        url = f"{self.base_url}/services/data/v{self.api_version}/query/"
        params = {"q": soql_query}

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                records = data.get("records", [])
                return self._convert_contact(records[0]) if records else None
            else:
                raise Exception(f"Failed to get contact: {response.status}")

    async def update_contact(self, contact_id: str, data: Dict[str, Any]) -> bool:
        """Update contact record"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        url = f"{self.base_url}/services/data/v{self.api_version}/sobjects/Contact/{contact_id}"

        async with self.session.patch(url, json=data) as response:
            return response.status == 204

    async def create_contact(self, contact: CRMContact) -> str:
        """Create new contact"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        contact_data = {
            "FirstName": contact.first_name,
            "LastName": contact.last_name,
            "Email": contact.email,
        }

        if contact.phone:
            contact_data["Phone"] = contact.phone
        if contact.company:
            contact_data["Company"] = contact.company
        if contact.title:
            contact_data["Title"] = contact.title
        if contact.lead_score:
            contact_data["LeadScore"] = contact.lead_score
        if contact.source:
            contact_data["LeadSource"] = contact.source

        url = f"{self.base_url}/services/data/v{self.api_version}/sobjects/Contact/"

        async with self.session.post(url, json=contact_data) as response:
            if response.status == 201:
                result = await response.json()
                return result["id"]
            else:
                raise Exception(f"Failed to create contact: {response.status}")

    async def get_opportunities(
        self, contact_id: Optional[str] = None
    ) -> List[CRMOpportunity]:
        """Retrieve opportunities"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        soql_query = """
            SELECT Id, Name, StageName, Amount, Probability, CloseDate, 
                   CreatedDate, ContactId
            FROM Opportunity
        """

        if contact_id:
            soql_query += f" WHERE ContactId = '{contact_id}'"

        url = f"{self.base_url}/services/data/v{self.api_version}/query/"
        params = {"q": soql_query}

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return [
                    self._convert_opportunity(record)
                    for record in data.get("records", [])
                ]
            else:
                raise Exception(f"Failed to get opportunities: {response.status}")

    async def get_accounts(self) -> List[CRMAccount]:
        """Retrieve accounts"""
        if not self.session:
            raise AuthenticationError("Not authenticated")

        soql_query = """
            SELECT Id, Name, Industry, Type, AnnualRevenue, Website, Phone,
                   BillingCity, BillingState, BillingCountry, CreatedDate
            FROM Account
        """

        url = f"{self.base_url}/services/data/v{self.api_version}/query/"
        params = {"q": soql_query}

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return [
                    self._convert_account(record) for record in data.get("records", [])
                ]
            else:
                raise Exception(f"Failed to get accounts: {response.status}")

    def _convert_contact(self, record: Dict[str, Any]) -> CRMContact:
        """Convert Salesforce contact to standard format"""
        return CRMContact(
            id=record["Id"],
            email=record.get("Email", ""),
            first_name=record.get("FirstName", ""),
            last_name=record.get("LastName", ""),
            phone=record.get("Phone"),
            company=record.get("Company"),
            title=record.get("Title"),
            lead_score=record.get("LeadScore"),
            source=record.get("LeadSource"),
            created_date=self._parse_date(record.get("CreatedDate")),
            last_updated=self._parse_date(record.get("LastModifiedDate")),
        )

    def _convert_opportunity(self, record: Dict[str, Any]) -> CRMOpportunity:
        """Convert Salesforce opportunity to standard format"""
        return CRMOpportunity(
            id=record["Id"],
            contact_id=record.get("ContactId"),
            name=record["Name"],
            stage=record["StageName"],
            value=record.get("Amount"),
            probability=record.get("Probability"),
            close_date=self._parse_date(record.get("CloseDate")),
            created_date=self._parse_date(record.get("CreatedDate")),
        )

    def _convert_account(self, record: Dict[str, Any]) -> CRMAccount:
        """Convert Salesforce account to standard format"""
        address = None
        if any(
            [
                record.get("BillingCity"),
                record.get("BillingState"),
                record.get("BillingCountry"),
            ]
        ):
            address = {
                "city": record.get("BillingCity"),
                "state": record.get("BillingState"),
                "country": record.get("BillingCountry"),
            }

        return CRMAccount(
            id=record["Id"],
            name=record["Name"],
            industry=record.get("Industry"),
            size=record.get("Type"),
            revenue=record.get("AnnualRevenue"),
            website=record.get("Website"),
            phone=record.get("Phone"),
            address=address,
            created_date=self._parse_date(record.get("CreatedDate")),
        )

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Salesforce datetime string"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            return None

    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
