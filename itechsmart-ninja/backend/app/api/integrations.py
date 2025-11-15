"""
Additional Integrations API Endpoints
Provides REST API for GitHub, Jira, Email, Calendar, CRM, and Cloud Storage integrations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

from ..services.integrations_service import (
    integrations_service,
    IntegrationType,
    SyncStatus
)

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


# Request Models
class ConnectIntegrationRequest(BaseModel):
    integration_type: IntegrationType
    name: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    config: Optional[dict] = None


class ExecuteActionRequest(BaseModel):
    action: str
    parameters: dict


# Response Models
class IntegrationResponse(BaseModel):
    success: bool
    integration: Optional[dict] = None
    error: Optional[str] = None


# Helper function
def get_current_user_id(user_id: str = Query(...)) -> str:
    """Get current authenticated user ID"""
    return user_id


# Connection Management

@router.post("/connect", response_model=IntegrationResponse)
async def connect_integration(
    workspace_id: str = Query(...),
    request: ConnectIntegrationRequest = None,
    user_id: str = Query(...)
):
    """
    Connect integration
    
    Supported integrations:
    - GitHub/GitLab (code repositories)
    - Jira/Trello (project management)
    - Gmail/Outlook (email)
    - Google Calendar/Outlook Calendar (scheduling)
    - Salesforce/HubSpot (CRM)
    - Dropbox/OneDrive (cloud storage)
    """
    result = integrations_service.connect_integration(
        workspace_id=workspace_id,
        integration_type=request.integration_type,
        name=request.name,
        user_id=user_id,
        access_token=request.access_token,
        refresh_token=request.refresh_token,
        token_expiry=request.token_expiry,
        config=request.config
    )
    
    return IntegrationResponse(**result)


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    user_id: str = Query(...)
):
    """
    Disconnect integration
    
    Removes integration connection
    """
    result = integrations_service.disconnect_integration(integration_id)
    return result


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: str,
    user_id: str = Query(...)
):
    """
    Get integration details
    
    Returns integration configuration and status
    """
    integration = integrations_service.get_integration(integration_id)
    
    if not integration:
        return IntegrationResponse(success=False, error="Integration not found")
    
    return IntegrationResponse(success=True, integration=integration.to_dict())


@router.get("/workspace/{workspace_id}/list")
async def list_integrations(
    workspace_id: str,
    integration_type: Optional[IntegrationType] = None,
    user_id: str = Query(...)
):
    """
    List workspace integrations
    
    Returns all connected integrations
    Optionally filter by integration type
    """
    integrations = integrations_service.list_workspace_integrations(
        workspace_id=workspace_id,
        integration_type=integration_type
    )
    
    return {
        "success": True,
        "integrations": integrations,
        "count": len(integrations)
    }


# GitHub Actions

@router.post("/{integration_id}/github/repositories")
async def list_github_repositories(
    integration_id: str,
    user_id: str = Query(...)
):
    """
    List GitHub repositories
    
    Returns user's repositories
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="list_repositories",
        parameters={}
    )
    
    return result


@router.post("/{integration_id}/github/create-issue")
async def create_github_issue(
    integration_id: str,
    repo: str = Query(...),
    title: str = Query(...),
    body: str = Query(...),
    user_id: str = Query(...)
):
    """
    Create GitHub issue
    
    Creates new issue in repository
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="create_issue",
        parameters={"repo": repo, "title": title, "body": body}
    )
    
    return result


@router.post("/{integration_id}/github/create-pr")
async def create_github_pr(
    integration_id: str,
    repo: str = Query(...),
    title: str = Query(...),
    body: str = Query(...),
    head: str = Query(...),
    base: str = Query("main"),
    user_id: str = Query(...)
):
    """
    Create GitHub pull request
    
    Creates new pull request
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="create_pull_request",
        parameters={
            "repo": repo,
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
    )
    
    return result


# Jira Actions

@router.post("/{integration_id}/jira/projects")
async def list_jira_projects(
    integration_id: str,
    user_id: str = Query(...)
):
    """
    List Jira projects
    
    Returns all accessible projects
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="list_projects",
        parameters={}
    )
    
    return result


@router.post("/{integration_id}/jira/create-issue")
async def create_jira_issue(
    integration_id: str,
    project_key: str = Query(...),
    summary: str = Query(...),
    description: str = Query(...),
    issue_type: str = Query("Task"),
    user_id: str = Query(...)
):
    """
    Create Jira issue
    
    Creates new issue in project
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="create_issue",
        parameters={
            "project_key": project_key,
            "summary": summary,
            "description": description,
            "issue_type": issue_type
        }
    )
    
    return result


# Email Actions

@router.post("/{integration_id}/email/send")
async def send_email(
    integration_id: str,
    to: List[EmailStr] = Query(...),
    subject: str = Query(...),
    body: str = Query(...),
    cc: Optional[List[EmailStr]] = None,
    user_id: str = Query(...)
):
    """
    Send email
    
    Sends email via Gmail or Outlook
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="send_email",
        parameters={
            "to": to,
            "subject": subject,
            "body": body,
            "cc": cc
        }
    )
    
    return result


@router.post("/{integration_id}/email/list")
async def list_emails(
    integration_id: str,
    folder: str = Query("inbox"),
    limit: int = Query(50, ge=1, le=100),
    user_id: str = Query(...)
):
    """
    List emails
    
    Returns emails from specified folder
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="list_emails",
        parameters={"folder": folder, "limit": limit}
    )
    
    return result


# Calendar Actions

@router.post("/{integration_id}/calendar/events")
async def list_calendar_events(
    integration_id: str,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    user_id: str = Query(...)
):
    """
    List calendar events
    
    Returns events in date range
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="list_events",
        parameters={"start_date": start_date, "end_date": end_date}
    )
    
    return result


@router.post("/{integration_id}/calendar/create-event")
async def create_calendar_event(
    integration_id: str,
    title: str = Query(...),
    start: datetime = Query(...),
    end: datetime = Query(...),
    description: Optional[str] = None,
    attendees: Optional[List[EmailStr]] = None,
    user_id: str = Query(...)
):
    """
    Create calendar event
    
    Creates new event in calendar
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="create_event",
        parameters={
            "title": title,
            "start": start,
            "end": end,
            "description": description,
            "attendees": attendees
        }
    )
    
    return result


# CRM Actions

@router.post("/{integration_id}/crm/contacts")
async def list_crm_contacts(
    integration_id: str,
    limit: int = Query(50, ge=1, le=100),
    user_id: str = Query(...)
):
    """
    List CRM contacts
    
    Returns contacts from Salesforce or HubSpot
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="list_contacts",
        parameters={"limit": limit}
    )
    
    return result


@router.post("/{integration_id}/crm/create-contact")
async def create_crm_contact(
    integration_id: str,
    data: dict = Query(...),
    user_id: str = Query(...)
):
    """
    Create CRM contact
    
    Creates new contact in CRM
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="create_contact",
        parameters={"data": data}
    )
    
    return result


# Cloud Storage Actions

@router.post("/{integration_id}/storage/files")
async def list_storage_files(
    integration_id: str,
    path: str = Query("/"),
    user_id: str = Query(...)
):
    """
    List cloud storage files
    
    Returns files from Dropbox or OneDrive
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="list_files",
        parameters={"path": path}
    )
    
    return result


@router.post("/{integration_id}/storage/upload")
async def upload_to_storage(
    integration_id: str,
    path: str = Query(...),
    content: bytes = Query(...),
    user_id: str = Query(...)
):
    """
    Upload file to cloud storage
    
    Uploads file to Dropbox or OneDrive
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action="upload_file",
        parameters={"path": path, "content": content}
    )
    
    return result


# Generic Action Execution

@router.post("/{integration_id}/execute")
async def execute_action(
    integration_id: str,
    request: ExecuteActionRequest,
    user_id: str = Query(...)
):
    """
    Execute integration action
    
    Generic endpoint for executing any integration action
    """
    result = integrations_service.execute_integration_action(
        integration_id=integration_id,
        action=request.action,
        parameters=request.parameters
    )
    
    return result


# Statistics

@router.get("/types")
async def list_integration_types():
    """
    List available integration types
    
    Returns all supported integrations
    """
    types = [
        {
            "value": it.value,
            "label": it.value.replace("_", " ").title(),
            "category": _get_integration_category(it)
        }
        for it in IntegrationType
    ]
    
    return {
        "success": True,
        "integration_types": types
    }


def _get_integration_category(integration_type: IntegrationType) -> str:
    """Get integration category"""
    if integration_type in [IntegrationType.GITHUB, IntegrationType.GITLAB]:
        return "Code Repository"
    elif integration_type in [IntegrationType.JIRA, IntegrationType.TRELLO]:
        return "Project Management"
    elif integration_type in [IntegrationType.GMAIL, IntegrationType.OUTLOOK]:
        return "Email"
    elif integration_type in [IntegrationType.GOOGLE_CALENDAR, IntegrationType.OUTLOOK_CALENDAR]:
        return "Calendar"
    elif integration_type in [IntegrationType.SALESFORCE, IntegrationType.HUBSPOT]:
        return "CRM"
    elif integration_type in [IntegrationType.DROPBOX, IntegrationType.ONEDRIVE]:
        return "Cloud Storage"
    return "Other"