"""
Google Drive Integration Service
Provides file sync, storage, and collaboration with Google Drive
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DriveFileType(str, Enum):
    """Google Drive file types"""

    DOCUMENT = "application/vnd.google-apps.document"
    SPREADSHEET = "application/vnd.google-apps.spreadsheet"
    PRESENTATION = "application/vnd.google-apps.presentation"
    FOLDER = "application/vnd.google-apps.folder"
    PDF = "application/pdf"
    IMAGE = "image/*"
    VIDEO = "video/*"
    AUDIO = "audio/*"
    TEXT = "text/plain"
    OTHER = "application/octet-stream"


class SyncDirection(str, Enum):
    """Sync direction"""

    UPLOAD = "upload"
    DOWNLOAD = "download"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, Enum):
    """Sync status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class DriveFile:
    """Google Drive file metadata"""

    file_id: str
    name: str
    mime_type: str
    size: int
    created_time: datetime
    modified_time: datetime
    parent_folder_id: Optional[str]
    web_view_link: str
    download_link: Optional[str]
    thumbnail_link: Optional[str]
    owners: List[str]
    shared: bool
    permissions: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "created_time": self.created_time.isoformat(),
            "modified_time": self.modified_time.isoformat(),
        }


@dataclass
class SyncTask:
    """File sync task"""

    task_id: str
    workspace_id: str
    local_path: str
    drive_file_id: Optional[str]
    direction: SyncDirection
    status: SyncStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error: Optional[str]
    bytes_transferred: int
    total_bytes: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "workspace_id": self.workspace_id,
            "local_path": self.local_path,
            "drive_file_id": self.drive_file_id,
            "direction": self.direction.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "error": self.error,
            "bytes_transferred": self.bytes_transferred,
            "total_bytes": self.total_bytes,
            "progress_percent": (
                (self.bytes_transferred / self.total_bytes * 100)
                if self.total_bytes > 0
                else 0
            ),
        }


@dataclass
class DriveConnection:
    """Google Drive connection"""

    connection_id: str
    workspace_id: str
    user_id: str
    access_token: str
    refresh_token: str
    token_expiry: datetime
    connected_at: datetime
    last_sync: Optional[datetime]
    sync_enabled: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connection_id": self.connection_id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "connected_at": self.connected_at.isoformat(),
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "sync_enabled": self.sync_enabled,
            "token_valid": datetime.utcnow() < self.token_expiry,
        }


class GoogleDriveClient:
    """Google Drive API client wrapper"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/drive/v3"

    def list_files(
        self,
        folder_id: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """List files in Drive"""
        # Mock implementation - in production, use Google Drive API
        return {
            "success": True,
            "files": [
                {
                    "id": "file_1",
                    "name": "Document.docx",
                    "mimeType": "application/vnd.google-apps.document",
                    "size": 1024,
                    "createdTime": datetime.utcnow().isoformat(),
                    "modifiedTime": datetime.utcnow().isoformat(),
                    "webViewLink": "https://drive.google.com/file/d/file_1",
                    "owners": ["user@example.com"],
                    "shared": False,
                }
            ],
            "nextPageToken": None,
        }

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata"""
        return {
            "success": True,
            "file": {
                "id": file_id,
                "name": "Document.docx",
                "mimeType": "application/vnd.google-apps.document",
                "size": 1024,
                "createdTime": datetime.utcnow().isoformat(),
                "modifiedTime": datetime.utcnow().isoformat(),
                "webViewLink": f"https://drive.google.com/file/d/{file_id}",
                "owners": ["user@example.com"],
                "shared": False,
            },
        }

    def download_file(self, file_id: str) -> bytes:
        """Download file content"""
        # Mock implementation
        return b"File content"

    def upload_file(
        self,
        file_name: str,
        file_content: bytes,
        mime_type: str,
        parent_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload file to Drive"""
        return {
            "success": True,
            "file": {
                "id": "new_file_id",
                "name": file_name,
                "mimeType": mime_type,
                "size": len(file_content),
                "webViewLink": "https://drive.google.com/file/d/new_file_id",
            },
        }

    def update_file(self, file_id: str, file_content: bytes) -> Dict[str, Any]:
        """Update file content"""
        return {
            "success": True,
            "file": {"id": file_id, "modifiedTime": datetime.utcnow().isoformat()},
        }

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete file"""
        return {"success": True, "file_id": file_id}

    def create_folder(
        self, folder_name: str, parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create folder"""
        return {
            "success": True,
            "folder": {
                "id": "new_folder_id",
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
            },
        }

    def share_file(
        self, file_id: str, email: str, role: str = "reader"
    ) -> Dict[str, Any]:
        """Share file with user"""
        return {
            "success": True,
            "permission": {"id": "permission_id", "email": email, "role": role},
        }


class GoogleDriveService:
    """Manages Google Drive integration"""

    def __init__(self):
        self.connections: Dict[str, DriveConnection] = {}
        self.sync_tasks: Dict[str, SyncTask] = {}
        self.workspace_connections: Dict[str, str] = {}  # workspace_id -> connection_id
        self.file_mappings: Dict[str, str] = {}  # local_path -> drive_file_id

    def connect_drive(
        self,
        workspace_id: str,
        user_id: str,
        access_token: str,
        refresh_token: str,
        token_expiry: datetime,
    ) -> Dict[str, Any]:
        """Connect Google Drive account"""
        try:
            import uuid

            connection_id = str(uuid.uuid4())

            connection = DriveConnection(
                connection_id=connection_id,
                workspace_id=workspace_id,
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expiry=token_expiry,
                connected_at=datetime.utcnow(),
                last_sync=None,
                sync_enabled=True,
            )

            self.connections[connection_id] = connection
            self.workspace_connections[workspace_id] = connection_id

            logger.info(f"Connected Google Drive for workspace {workspace_id}")

            return {"success": True, "connection": connection.to_dict()}

        except Exception as e:
            logger.error(f"Failed to connect Drive: {e}")
            return {"success": False, "error": str(e)}

    def disconnect_drive(self, workspace_id: str) -> Dict[str, Any]:
        """Disconnect Google Drive"""
        connection_id = self.workspace_connections.get(workspace_id)
        if not connection_id:
            return {"success": False, "error": "Not connected"}

        try:
            del self.connections[connection_id]
            del self.workspace_connections[workspace_id]

            logger.info(f"Disconnected Google Drive for workspace {workspace_id}")

            return {"success": True, "workspace_id": workspace_id}

        except Exception as e:
            logger.error(f"Failed to disconnect Drive: {e}")
            return {"success": False, "error": str(e)}

    def get_connection(self, workspace_id: str) -> Optional[DriveConnection]:
        """Get Drive connection for workspace"""
        connection_id = self.workspace_connections.get(workspace_id)
        return self.connections.get(connection_id) if connection_id else None

    def list_files(
        self,
        workspace_id: str,
        folder_id: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """List files in Google Drive"""
        connection = self.get_connection(workspace_id)
        if not connection:
            return {"success": False, "error": "Not connected to Google Drive"}

        try:
            client = GoogleDriveClient(connection.access_token)
            result = client.list_files(folder_id, query, page_size)

            if result["success"]:
                files = []
                for file_data in result["files"]:
                    drive_file = DriveFile(
                        file_id=file_data["id"],
                        name=file_data["name"],
                        mime_type=file_data["mimeType"],
                        size=file_data.get("size", 0),
                        created_time=datetime.fromisoformat(
                            file_data["createdTime"].replace("Z", "+00:00")
                        ),
                        modified_time=datetime.fromisoformat(
                            file_data["modifiedTime"].replace("Z", "+00:00")
                        ),
                        parent_folder_id=folder_id,
                        web_view_link=file_data["webViewLink"],
                        download_link=file_data.get("downloadLink"),
                        thumbnail_link=file_data.get("thumbnailLink"),
                        owners=file_data["owners"],
                        shared=file_data["shared"],
                        permissions=[],
                    )
                    files.append(drive_file.to_dict())

                return {
                    "success": True,
                    "files": files,
                    "nextPageToken": result.get("nextPageToken"),
                }

            return result

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return {"success": False, "error": str(e)}

    def download_file(
        self, workspace_id: str, file_id: str, local_path: str
    ) -> Dict[str, Any]:
        """Download file from Google Drive"""
        connection = self.get_connection(workspace_id)
        if not connection:
            return {"success": False, "error": "Not connected to Google Drive"}

        try:
            import uuid

            # Create sync task
            task_id = str(uuid.uuid4())
            task = SyncTask(
                task_id=task_id,
                workspace_id=workspace_id,
                local_path=local_path,
                drive_file_id=file_id,
                direction=SyncDirection.DOWNLOAD,
                status=SyncStatus.IN_PROGRESS,
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                completed_at=None,
                error=None,
                bytes_transferred=0,
                total_bytes=0,
            )

            self.sync_tasks[task_id] = task

            # Download file
            client = GoogleDriveClient(connection.access_token)
            file_content = client.download_file(file_id)

            # Save to local path
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(file_content)

            # Update task
            task.status = SyncStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.bytes_transferred = len(file_content)
            task.total_bytes = len(file_content)

            # Store mapping
            self.file_mappings[local_path] = file_id

            connection.last_sync = datetime.utcnow()

            logger.info(f"Downloaded file {file_id} to {local_path}")

            return {"success": True, "task": task.to_dict(), "local_path": local_path}

        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            if task_id in self.sync_tasks:
                self.sync_tasks[task_id].status = SyncStatus.FAILED
                self.sync_tasks[task_id].error = str(e)
            return {"success": False, "error": str(e)}

    def upload_file(
        self,
        workspace_id: str,
        local_path: str,
        drive_folder_id: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload file to Google Drive"""
        connection = self.get_connection(workspace_id)
        if not connection:
            return {"success": False, "error": "Not connected to Google Drive"}

        try:
            import uuid
            import mimetypes

            # Read local file
            if not Path(local_path).exists():
                return {"success": False, "error": "Local file not found"}

            with open(local_path, "rb") as f:
                file_content = f.read()

            # Determine file name and mime type
            file_name = file_name or Path(local_path).name
            mime_type = (
                mimetypes.guess_type(local_path)[0] or "application/octet-stream"
            )

            # Create sync task
            task_id = str(uuid.uuid4())
            task = SyncTask(
                task_id=task_id,
                workspace_id=workspace_id,
                local_path=local_path,
                drive_file_id=None,
                direction=SyncDirection.UPLOAD,
                status=SyncStatus.IN_PROGRESS,
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                completed_at=None,
                error=None,
                bytes_transferred=0,
                total_bytes=len(file_content),
            )

            self.sync_tasks[task_id] = task

            # Upload file
            client = GoogleDriveClient(connection.access_token)
            result = client.upload_file(
                file_name, file_content, mime_type, drive_folder_id
            )

            if result["success"]:
                file_id = result["file"]["id"]

                # Update task
                task.drive_file_id = file_id
                task.status = SyncStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.bytes_transferred = len(file_content)

                # Store mapping
                self.file_mappings[local_path] = file_id

                connection.last_sync = datetime.utcnow()

                logger.info(f"Uploaded file {local_path} to Drive as {file_id}")

                return {"success": True, "task": task.to_dict(), "file": result["file"]}

            return result

        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            if task_id in self.sync_tasks:
                self.sync_tasks[task_id].status = SyncStatus.FAILED
                self.sync_tasks[task_id].error = str(e)
            return {"success": False, "error": str(e)}

    def sync_folder(
        self,
        workspace_id: str,
        local_folder: str,
        drive_folder_id: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
    ) -> Dict[str, Any]:
        """Sync entire folder with Google Drive"""
        connection = self.get_connection(workspace_id)
        if not connection:
            return {"success": False, "error": "Not connected to Google Drive"}

        try:
            synced_files = []
            errors = []

            # Get local files
            local_path = Path(local_folder)
            if not local_path.exists():
                local_path.mkdir(parents=True, exist_ok=True)

            # Upload local files
            if direction in [SyncDirection.UPLOAD, SyncDirection.BIDIRECTIONAL]:
                for file_path in local_path.rglob("*"):
                    if file_path.is_file():
                        result = self.upload_file(
                            workspace_id=workspace_id,
                            local_path=str(file_path),
                            drive_folder_id=drive_folder_id,
                        )

                        if result["success"]:
                            synced_files.append(result)
                        else:
                            errors.append(result)

            # Download Drive files
            if direction in [SyncDirection.DOWNLOAD, SyncDirection.BIDIRECTIONAL]:
                files_result = self.list_files(workspace_id, drive_folder_id)

                if files_result["success"]:
                    for file_data in files_result["files"]:
                        if file_data["mime_type"] != DriveFileType.FOLDER.value:
                            local_file_path = str(local_path / file_data["name"])

                            result = self.download_file(
                                workspace_id=workspace_id,
                                file_id=file_data["file_id"],
                                local_path=local_file_path,
                            )

                            if result["success"]:
                                synced_files.append(result)
                            else:
                                errors.append(result)

            connection.last_sync = datetime.utcnow()

            return {
                "success": True,
                "synced_files": len(synced_files),
                "errors": len(errors),
                "details": {"synced": synced_files, "errors": errors},
            }

        except Exception as e:
            logger.error(f"Failed to sync folder: {e}")
            return {"success": False, "error": str(e)}

    def get_sync_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get sync task status"""
        task = self.sync_tasks.get(task_id)
        return task.to_dict() if task else None

    def list_sync_tasks(
        self, workspace_id: str, status: Optional[SyncStatus] = None
    ) -> List[Dict[str, Any]]:
        """List sync tasks for workspace"""
        tasks = []

        for task in self.sync_tasks.values():
            if task.workspace_id == workspace_id:
                if status is None or task.status == status:
                    tasks.append(task.to_dict())

        return tasks

    def create_folder(
        self,
        workspace_id: str,
        folder_name: str,
        parent_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create folder in Google Drive"""
        connection = self.get_connection(workspace_id)
        if not connection:
            return {"success": False, "error": "Not connected to Google Drive"}

        try:
            client = GoogleDriveClient(connection.access_token)
            result = client.create_folder(folder_name, parent_folder_id)

            logger.info(f"Created folder {folder_name} in Drive")

            return result

        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return {"success": False, "error": str(e)}

    def share_file(
        self, workspace_id: str, file_id: str, email: str, role: str = "reader"
    ) -> Dict[str, Any]:
        """Share file with user"""
        connection = self.get_connection(workspace_id)
        if not connection:
            return {"success": False, "error": "Not connected to Google Drive"}

        try:
            client = GoogleDriveClient(connection.access_token)
            result = client.share_file(file_id, email, role)

            logger.info(f"Shared file {file_id} with {email}")

            return result

        except Exception as e:
            logger.error(f"Failed to share file: {e}")
            return {"success": False, "error": str(e)}


# Global service instance
google_drive_service = GoogleDriveService()
