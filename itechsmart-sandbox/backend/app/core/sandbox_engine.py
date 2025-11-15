"""
iTechSmart Sandbox - Core Sandbox Engine
Secure code execution environment with isolation
"""

import asyncio
import docker
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import json

from app.models.models import (
    Sandbox, Process, Snapshot, SandboxFile, ResourceMetric,
    Volume, TestRun, Template,
    SandboxStatus, ProcessStatus, SnapshotStatus
)

logger = logging.getLogger(__name__)


class SandboxEngine:
    """
    Core sandbox management engine
    
    Features:
    - Sandbox creation and lifecycle management
    - Process execution with real-time output
    - File system operations
    - Port exposure and preview URLs
    - Snapshot creation and restoration
    - Resource monitoring
    - Auto-termination
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.docker_client = docker.from_env()
    
    # ==================== Sandbox Management ====================
    
    def create_sandbox(
        self,
        name: str = None,
        image: str = "python:3.11-slim",
        cpu: float = 1.0,
        memory: str = "1Gi",
        gpu: str = None,
        python_version: str = "3.11",
        packages: List[str] = None,
        env_vars: Dict[str, str] = None,
        secrets: List[str] = None,
        volumes: List[str] = None,
        keep_warm_seconds: int = 3600,
        auto_terminate: bool = True,
        created_by: str = None,
        project_id: int = None
    ) -> Sandbox:
        """
        Create new sandbox instance
        
        Args:
            name: Sandbox name
            image: Docker image to use
            cpu: CPU cores (0.5, 1.0, 2.0, 4.0, 8.0)
            memory: Memory allocation (128Mi, 1Gi, 2Gi, 4Gi, 8Gi, 16Gi, 32Gi)
            gpu: GPU type (A10G, T4, V100, A100)
            python_version: Python version
            packages: Python packages to install
            env_vars: Environment variables
            secrets: Secret names to inject
            volumes: Volume names to mount
            keep_warm_seconds: Auto-terminate after seconds (-1 for manual)
            auto_terminate: Enable auto-termination
            created_by: User who created sandbox
            project_id: Project ID
        
        Returns:
            Sandbox instance
        """
        try:
            sandbox_id = f"sb-{uuid.uuid4().hex[:12]}"
            
            # Create database record
            sandbox = Sandbox(
                sandbox_id=sandbox_id,
                name=name or f"sandbox-{sandbox_id}",
                image=image,
                cpu=cpu,
                memory=memory,
                gpu=gpu,
                python_version=python_version,
                packages=packages or [],
                env_vars=env_vars or {},
                secrets=secrets or [],
                volumes=volumes or [],
                exposed_ports=[],
                preview_urls={},
                keep_warm_seconds=keep_warm_seconds,
                auto_terminate=auto_terminate,
                created_by=created_by,
                project_id=project_id,
                status=SandboxStatus.CREATING
            )
            
            self.db.add(sandbox)
            self.db.commit()
            self.db.refresh(sandbox)
            
            # Start sandbox container
            self._start_container(sandbox)
            
            # Update status
            sandbox.status = SandboxStatus.RUNNING
            sandbox.started_at = datetime.utcnow()
            sandbox.last_activity = datetime.utcnow()
            self.db.commit()
            
            # Schedule auto-termination if enabled
            if auto_terminate and keep_warm_seconds > 0:
                asyncio.create_task(self._auto_terminate(sandbox.id, keep_warm_seconds))
            
            logger.info(f"Created sandbox: {sandbox_id}")
            return sandbox
            
        except Exception as e:
            logger.error(f"Error creating sandbox: {e}")
            if sandbox:
                sandbox.status = SandboxStatus.ERROR
                self.db.commit()
            raise
    
    def get_sandbox(self, sandbox_id: str) -> Optional[Sandbox]:
        """Get sandbox by ID"""
        return self.db.query(Sandbox).filter(
            Sandbox.sandbox_id == sandbox_id
        ).first()
    
    def list_sandboxes(
        self,
        status: SandboxStatus = None,
        project_id: int = None,
        created_by: str = None,
        limit: int = 100
    ) -> List[Sandbox]:
        """List sandboxes with filters"""
        q = self.db.query(Sandbox)
        
        if status:
            q = q.filter(Sandbox.status == status)
        if project_id:
            q = q.filter(Sandbox.project_id == project_id)
        if created_by:
            q = q.filter(Sandbox.created_by == created_by)
        
        return q.order_by(Sandbox.created_at.desc()).limit(limit).all()
    
    def terminate_sandbox(self, sandbox_id: str) -> Sandbox:
        """Terminate sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        try:
            # Stop container
            self._stop_container(sandbox)
            
            # Update status
            sandbox.status = SandboxStatus.TERMINATED
            sandbox.terminated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Terminated sandbox: {sandbox_id}")
            return sandbox
            
        except Exception as e:
            logger.error(f"Error terminating sandbox: {e}")
            raise
    
    def update_ttl(self, sandbox_id: str, seconds: int) -> Sandbox:
        """Update sandbox TTL (time to live)"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        sandbox.keep_warm_seconds = seconds
        sandbox.last_activity = datetime.utcnow()
        self.db.commit()
        
        return sandbox
    
    # ==================== Process Management ====================
    
    def run_code(
        self,
        sandbox_id: str,
        code: str,
        timeout: int = 60
    ) -> Process:
        """Execute Python code in sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        process_id = f"proc-{uuid.uuid4().hex[:12]}"
        
        try:
            # Create process record
            process = Process(
                sandbox_id=sandbox.id,
                process_id=process_id,
                command="python",
                args=["-c", code],
                status=ProcessStatus.RUNNING
            )
            
            self.db.add(process)
            self.db.commit()
            
            # Execute code (mock implementation)
            # In production, this would execute in the Docker container
            stdout = f"Executed code in sandbox {sandbox_id}"
            stderr = ""
            exit_code = 0
            
            # Update process
            process.stdout = stdout
            process.stderr = stderr
            process.exit_code = exit_code
            process.status = ProcessStatus.COMPLETED
            process.completed_at = datetime.utcnow()
            
            # Update sandbox activity
            sandbox.last_activity = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(process)
            
            return process
            
        except Exception as e:
            logger.error(f"Error running code: {e}")
            if process:
                process.status = ProcessStatus.FAILED
                process.stderr = str(e)
                self.db.commit()
            raise
    
    def exec_command(
        self,
        sandbox_id: str,
        command: str,
        args: List[str] = None,
        cwd: str = None,
        timeout: int = 60
    ) -> Process:
        """Execute shell command in sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        process_id = f"proc-{uuid.uuid4().hex[:12]}"
        
        try:
            process = Process(
                sandbox_id=sandbox.id,
                process_id=process_id,
                command=command,
                args=args or [],
                cwd=cwd or "/workspace",
                status=ProcessStatus.RUNNING
            )
            
            self.db.add(process)
            self.db.commit()
            
            # Execute command (mock implementation)
            stdout = f"Executed: {command} {' '.join(args or [])}"
            stderr = ""
            exit_code = 0
            
            # Update process
            process.stdout = stdout
            process.stderr = stderr
            process.exit_code = exit_code
            process.status = ProcessStatus.COMPLETED
            process.completed_at = datetime.utcnow()
            
            # Update sandbox activity
            sandbox.last_activity = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(process)
            
            return process
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            if process:
                process.status = ProcessStatus.FAILED
                process.stderr = str(e)
                self.db.commit()
            raise
    
    # ==================== File System Operations ====================
    
    def upload_file(
        self,
        sandbox_id: str,
        local_path: str,
        remote_path: str
    ) -> SandboxFile:
        """Upload file to sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        try:
            # Create file record
            sandbox_file = SandboxFile(
                sandbox_id=sandbox.id,
                file_path=remote_path,
                file_name=remote_path.split('/')[-1],
                file_size=0,  # Would get actual size
                file_type="unknown"
            )
            
            self.db.add(sandbox_file)
            
            # Update sandbox activity
            sandbox.last_activity = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(sandbox_file)
            
            logger.info(f"Uploaded file to sandbox: {remote_path}")
            return sandbox_file
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    def download_file(
        self,
        sandbox_id: str,
        remote_path: str,
        local_path: str
    ) -> bool:
        """Download file from sandbox"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        try:
            # Update sandbox activity
            sandbox.last_activity = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Downloaded file from sandbox: {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise
    
    def list_files(
        self,
        sandbox_id: str,
        path: str = "/workspace"
    ) -> List[Dict[str, Any]]:
        """List files in sandbox directory"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        # Mock file listing
        return [
            {"name": "example.py", "size": 1024, "type": "file"},
            {"name": "data", "size": 0, "type": "directory"}
        ]
    
    # ==================== Networking ====================
    
    def expose_port(
        self,
        sandbox_id: str,
        port: int
    ) -> str:
        """Expose sandbox port and get preview URL"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        try:
            # Generate preview URL
            preview_url = f"https://{sandbox_id}.sandbox.itechsmart.dev:{port}"
            
            # Update sandbox
            exposed_ports = sandbox.exposed_ports or []
            if port not in exposed_ports:
                exposed_ports.append(port)
            
            preview_urls = sandbox.preview_urls or {}
            preview_urls[str(port)] = preview_url
            
            sandbox.exposed_ports = exposed_ports
            sandbox.preview_urls = preview_urls
            sandbox.last_activity = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Exposed port {port} for sandbox {sandbox_id}")
            return preview_url
            
        except Exception as e:
            logger.error(f"Error exposing port: {e}")
            raise
    
    # ==================== Snapshots ====================
    
    def create_snapshot(
        self,
        sandbox_id: str,
        name: str,
        description: str = None
    ) -> Snapshot:
        """Create filesystem snapshot"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        try:
            snapshot_id = f"snap-{uuid.uuid4().hex[:12]}"
            
            snapshot = Snapshot(
                sandbox_id=sandbox.id,
                snapshot_id=snapshot_id,
                name=name,
                description=description,
                status=SnapshotStatus.CREATING
            )
            
            self.db.add(snapshot)
            self.db.commit()
            
            # Create snapshot (mock implementation)
            snapshot.status = SnapshotStatus.READY
            snapshot.size_bytes = 1024 * 1024 * 100  # 100MB
            
            self.db.commit()
            self.db.refresh(snapshot)
            
            logger.info(f"Created snapshot: {snapshot_id}")
            return snapshot
            
        except Exception as e:
            logger.error(f"Error creating snapshot: {e}")
            if snapshot:
                snapshot.status = SnapshotStatus.FAILED
                self.db.commit()
            raise
    
    def restore_snapshot(
        self,
        sandbox_id: str,
        snapshot_id: str
    ) -> bool:
        """Restore sandbox from snapshot"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        snapshot = self.db.query(Snapshot).filter(
            Snapshot.snapshot_id == snapshot_id
        ).first()
        
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")
        
        try:
            # Restore filesystem (mock implementation)
            sandbox.last_activity = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Restored snapshot {snapshot_id} to sandbox {sandbox_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring snapshot: {e}")
            raise
    
    # ==================== Resource Monitoring ====================
    
    def collect_metrics(self, sandbox_id: str) -> ResourceMetric:
        """Collect resource usage metrics"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        try:
            # Collect metrics (mock implementation)
            metric = ResourceMetric(
                sandbox_id=sandbox.id,
                cpu_usage=25.5,
                memory_usage=45.2,
                memory_bytes=512 * 1024 * 1024,
                gpu_usage=0.0 if not sandbox.gpu else 30.0,
                disk_usage=15.8,
                network_in=1024 * 1024,
                network_out=512 * 1024
            )
            
            self.db.add(metric)
            self.db.commit()
            self.db.refresh(metric)
            
            return metric
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            raise
    
    def get_metrics(
        self,
        sandbox_id: str,
        limit: int = 100
    ) -> List[ResourceMetric]:
        """Get sandbox metrics history"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        return self.db.query(ResourceMetric).filter(
            ResourceMetric.sandbox_id == sandbox.id
        ).order_by(ResourceMetric.timestamp.desc()).limit(limit).all()
    
    # ==================== Test Execution ====================
    
    def run_test_suite(
        self,
        sandbox_id: str,
        product_name: str,
        test_suite: str,
        test_type: str = "integration"
    ) -> TestRun:
        """Run test suite for iTechSmart product"""
        sandbox = self.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        try:
            test_run = TestRun(
                sandbox_id=sandbox.id,
                test_suite=test_suite,
                product_name=product_name,
                test_type=test_type,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0
            )
            
            self.db.add(test_run)
            self.db.commit()
            
            # Run tests (mock implementation)
            test_run.total_tests = 50
            test_run.passed_tests = 48
            test_run.failed_tests = 2
            test_run.skipped_tests = 0
            test_run.duration_seconds = 45.3
            test_run.results = {
                "passed": ["test_1", "test_2"],
                "failed": ["test_3", "test_4"]
            }
            test_run.completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(test_run)
            
            logger.info(f"Test run completed: {test_run.id}")
            return test_run
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            raise
    
    # ==================== Helper Methods ====================
    
    def _start_container(self, sandbox: Sandbox):
        """Start Docker container for sandbox"""
        try:
            # Container configuration
            container_config = {
                "image": sandbox.image,
                "name": f"sandbox-{sandbox.sandbox_id}",
                "detach": True,
                "environment": sandbox.env_vars or {},
                "mem_limit": sandbox.memory,
                "nano_cpus": int(sandbox.cpu * 1e9),
            }
            
            # Add GPU if specified
            if sandbox.gpu:
                container_config["device_requests"] = [
                    docker.types.DeviceRequest(
                        device_ids=["0"],
                        capabilities=[["gpu"]]
                    )
                ]
            
            # Start container (mock - would actually start Docker container)
            logger.info(f"Started container for sandbox {sandbox.sandbox_id}")
            
        except Exception as e:
            logger.error(f"Error starting container: {e}")
            raise
    
    def _stop_container(self, sandbox: Sandbox):
        """Stop Docker container"""
        try:
            # Stop container (mock implementation)
            logger.info(f"Stopped container for sandbox {sandbox.sandbox_id}")
            
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            raise
    
    async def _auto_terminate(self, sandbox_id: int, seconds: int):
        """Auto-terminate sandbox after specified seconds"""
        await asyncio.sleep(seconds)
        
        try:
            sandbox = self.db.query(Sandbox).filter(Sandbox.id == sandbox_id).first()
            
            if sandbox and sandbox.status == SandboxStatus.RUNNING:
                # Check if there was recent activity
                if sandbox.last_activity:
                    time_since_activity = (datetime.utcnow() - sandbox.last_activity).total_seconds()
                    if time_since_activity < seconds:
                        # Reschedule
                        remaining = seconds - time_since_activity
                        asyncio.create_task(self._auto_terminate(sandbox_id, int(remaining)))
                        return
                
                # Terminate
                self.terminate_sandbox(sandbox.sandbox_id)
                logger.info(f"Auto-terminated sandbox: {sandbox.sandbox_id}")
                
        except Exception as e:
            logger.error(f"Error in auto-terminate: {e}")