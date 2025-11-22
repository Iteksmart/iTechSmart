"""
CRM Integrations Module for iTechSmart CDP
Connectors for popular CRM platforms including Salesforce, HubSpot, Marketo, and more
"""

from .salesforce_connector import SalesforceConnector
from .hubspot_connector import HubSpotConnector
from .marketo_connector import MarketoConnector
from .base_crm import BaseCRMConnector

__all__ = [
    'BaseCRMConnector',
    'SalesforceConnector', 
    'HubSpotConnector',
    'MarketoConnector'
]