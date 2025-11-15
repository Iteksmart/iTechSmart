"""
Sandbox Environment Manager for iTechSmart Ninja
Provides secure, isolated Docker-based execution environments
"""

import docker
import asyncio
import uuid
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class SandboxStatus(str, Enum):
    """Sandbox lifecycle states"""
    CREATING = "creating"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"


class SandboxLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    RUBY = "ruby"
    PHP = "php"


@dataclass
class SandboxConfig:
    """Configuration for sandbox environment"""
    language: SandboxLanguage
    memory_limit: str = "512m"  # Memory limit (e.g., "512m", "1g")
    cpu_limit: float = 1.0  # CPU cores
    timeout: int = 300  # Execution timeout in seconds
    network_enabled: bool = False  # Network access
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    max_output_size: int = 1024 * 1024  # 1MB
    environment_vars: Dict[str, str] = None
    
    def __post_init__(self):
        if self.environment_vars is None:
            self.environment_vars = {}


@dataclass
class SandboxInfo:
    """Information about a sandbox instance"""
    sandbox_id: str
    language: SandboxLanguage
    status: SandboxStatus
    container_id: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]
    config: SandboxConfig
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['stopped_at'] = self.stopped_at.isoformat() if self.stopped_at else None
        data['config'] = asdict(self.config)
        return data


@dataclass
class ExecutionResult:
    """Result of code execution in sandbox"""
    sandbox_id: str
    success: bool
    output: str
    error: Optional[str]
    exit_code: int
    execution_time: float
    memory_used: Optional[int]
    cpu_used: Optional[float]


class SandboxManager:
    """Manages Docker-based sandbox environments"""
    
    # Docker images for different languages
    LANGUAGE_IMAGES = {
        SandboxLanguage.PYTHON: "python:3.11-slim",
        SandboxLanguage.JAVASCRIPT: "node:20-slim",
        SandboxLanguage.TYPESCRIPT: "node:20-slim",
        SandboxLanguage.JAVA: "openjdk:17-slim",
        SandboxLanguage.GO: "golang:1.21-alpine",
        SandboxLanguage.RUST: "rust:1.75-slim",
        SandboxLanguage.CPP: "gcc:13-slim",
        SandboxLanguage.RUBY: "ruby:3.2-slim",
        SandboxLanguage.PHP: "php:8.2-cli-alpine",
    }
    
    def __init__(self):
        """Initialize sandbox manager"""
        try:
            self.client = docker.from_env()
            self.sandboxes: Dict[str, SandboxInfo] = {}
            self.containers: Dict[str, Any] = {}
            logger.info("SandboxManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
    
    async def create_sandbox(
        self,
        language: SandboxLanguage,
        config: Optional[SandboxConfig] = None
    ) -> SandboxInfo:
        """
        Create a new sandbox environment
        
        Args:
            language: Programming language for the sandbox
            config: Optional sandbox configuration
            
        Returns:
            SandboxInfo object with sandbox details
        """
        sandbox_id = str(uuid.uuid4())
        
        if config is None:
            config = SandboxConfig(language=language)
        
        sandbox_info = SandboxInfo(
            sandbox_id=sandbox_id,
            language=language,
            status=SandboxStatus.CREATING,
            container_id=None,
            created_at=datetime.now(),
            started_at=None,
            stopped_at=None,
            config=config
        )
        
        self.sandboxes[sandbox_id] = sandbox_info
        
        try:
            # Get Docker image for language
            image = self.LANGUAGE_IMAGES.get(language)
            if not image:
                raise ValueError(f"Unsupported language: {language}")
            
            # Pull image if not available
            try:
                self.client.images.get(image)
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling Docker image: {image}")
                self.client.images.pull(image)
            
            # Create container
            container = self.client.containers.create(
                image=image,
                name=f"sandbox-{sandbox_id[:8]}",
                detach=True,
                mem_limit=config.memory_limit,
                nano_cpus=int(config.cpu_limit * 1e9),
                network_disabled=not config.network_enabled,
                environment=config.environment_vars,
                command="tail -f /dev/null",  # Keep container running
                labels={
                    "sandbox_id": sandbox_id,
                    "language": language.value,
                    "managed_by": "itechsmart-ninja"
                }
            )
            
            # Start container
            container.start()
            
            # Update sandbox info
            sandbox_info.container_id = container.id
            sandbox_info.status = SandboxStatus.READY
            sandbox_info.started_at = datetime.now()
            
            self.containers[sandbox_id] = container
            
            logger.info(f"Sandbox {sandbox_id} created successfully")
            return sandbox_info
            
        except Exception as e:
            logger.error(f"Failed to create sandbox {sandbox_id}: {e}")
            sandbox_info.status = SandboxStatus.ERROR
            sandbox_info.error_message = str(e)
            raise
    
    async def execute_code(
        self,
        sandbox_id: str,
        code: str,
        filename: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute code in a sandbox
        
        Args:
            sandbox_id: ID of the sandbox
            code: Code to execute
            filename: Optional filename for the code
            
        Returns:
            ExecutionResult with execution details
        """
        sandbox_info = self.sandboxes.get(sandbox_id)
        if not sandbox_info:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        if sandbox_info.status != SandboxStatus.READY:
            raise ValueError(f"Sandbox {sandbox_id} is not ready (status: {sandbox_info.status})")
        
        container = self.containers.get(sandbox_id)
        if not container:
            raise ValueError(f"Container for sandbox {sandbox_id} not found")
        
        start_time = time.time()
        
        try:
            # Update status
            sandbox_info.status = SandboxStatus.RUNNING
            
            # Determine execution command based on language
            language = sandbox_info.language
            
            if filename is None:
                filename = self._get_default_filename(language)
            
            # Write code to file in container
            exec_result = container.exec_run(
                f"sh -c 'cat > /tmp/{filename}'",
                stdin=True,
                socket=True
            )
            exec_result.output._sock.sendall(code.encode())
            exec_result.output._sock.close()
            
            # Execute code
            command = self._get_execution_command(language, filename)
            exec_result = container.exec_run(
                command,
                workdir="/tmp",
                demux=True
            )
            
            execution_time = time.time() - start_time
            
            # Get output
            stdout, stderr = exec_result.output
            output = (stdout.decode() if stdout else "") + (stderr.decode() if stderr else "")
            
            # Truncate output if too large
            max_output = sandbox_info.config.max_output_size
            if len(output) > max_output:
                output = output[:max_output] + f"\n... (output truncated, {len(output)} bytes total)"
            
            # Get resource usage
            stats = container.stats(stream=False)
            memory_used = stats.get('memory_stats', {}).get('usage', 0)
            cpu_used = self._calculate_cpu_usage(stats)
            
            # Update status
            sandbox_info.status = SandboxStatus.READY
            
            return ExecutionResult(
                sandbox_id=sandbox_id,
                success=exec_result.exit_code == 0,
                output=output,
                error=stderr.decode() if stderr and exec_result.exit_code != 0 else None,
                exit_code=exec_result.exit_code,
                execution_time=execution_time,
                memory_used=memory_used,
                cpu_used=cpu_used
            )
            
        except Exception as e:
            logger.error(f"Failed to execute code in sandbox {sandbox_id}: {e}")
            sandbox_info.status = SandboxStatus.ERROR
            sandbox_info.error_message = str(e)
            
            return ExecutionResult(
                sandbox_id=sandbox_id,
                success=False,
                output="",
                error=str(e),
                exit_code=-1,
                execution_time=time.time() - start_time,
                memory_used=None,
                cpu_used=None
            )
    
    async def stop_sandbox(self, sandbox_id: str) -> bool:
        """
        Stop a sandbox
        
        Args:
            sandbox_id: ID of the sandbox to stop
            
        Returns:
            True if successful
        """
        sandbox_info = self.sandboxes.get(sandbox_id)
        if not sandbox_info:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        container = self.containers.get(sandbox_id)
        if not container:
            raise ValueError(f"Container for sandbox {sandbox_id} not found")
        
        try:
            container.stop(timeout=10)
            sandbox_info.status = SandboxStatus.STOPPED
            sandbox_info.stopped_at = datetime.now()
            logger.info(f"Sandbox {sandbox_id} stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop sandbox {sandbox_id}: {e}")
            raise
    
    async def terminate_sandbox(self, sandbox_id: str) -> bool:
        """
        Terminate and remove a sandbox
        
        Args:
            sandbox_id: ID of the sandbox to terminate
            
        Returns:
            True if successful
        """
        sandbox_info = self.sandboxes.get(sandbox_id)
        if not sandbox_info:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        container = self.containers.get(sandbox_id)
        if not container:
            raise ValueError(f"Container for sandbox {sandbox_id} not found")
        
        try:
            # Stop container if running
            if sandbox_info.status in [SandboxStatus.READY, SandboxStatus.RUNNING]:
                container.stop(timeout=10)
            
            # Remove container
            container.remove(force=True)
            
            # Update status
            sandbox_info.status = SandboxStatus.TERMINATED
            sandbox_info.stopped_at = datetime.now()
            
            # Clean up
            del self.containers[sandbox_id]
            
            logger.info(f"Sandbox {sandbox_id} terminated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to terminate sandbox {sandbox_id}: {e}")
            raise
    
    async def get_sandbox_info(self, sandbox_id: str) -> Optional[SandboxInfo]:
        """Get information about a sandbox"""
        return self.sandboxes.get(sandbox_id)
    
    async def list_sandboxes(
        self,
        status: Optional[SandboxStatus] = None,
        language: Optional[SandboxLanguage] = None
    ) -> List[SandboxInfo]:
        """
        List all sandboxes with optional filtering
        
        Args:
            status: Filter by status
            language: Filter by language
            
        Returns:
            List of SandboxInfo objects
        """
        sandboxes = list(self.sandboxes.values())
        
        if status:
            sandboxes = [s for s in sandboxes if s.status == status]
        
        if language:
            sandboxes = [s for s in sandboxes if s.language == language]
        
        return sandboxes
    
    async def cleanup_old_sandboxes(self, max_age_hours: int = 24) -> int:
        """
        Clean up sandboxes older than specified age
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of sandboxes cleaned up
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned = 0
        
        for sandbox_id, sandbox_info in list(self.sandboxes.items()):
            if sandbox_info.created_at < cutoff_time:
                try:
                    await self.terminate_sandbox(sandbox_id)
                    cleaned += 1
                except Exception as e:
                    logger.error(f"Failed to cleanup sandbox {sandbox_id}: {e}")
        
        logger.info(f"Cleaned up {cleaned} old sandboxes")
        return cleaned
    
    def _get_default_filename(self, language: SandboxLanguage) -> str:
        """Get default filename for language"""
        extensions = {
            SandboxLanguage.PYTHON: "main.py",
            SandboxLanguage.JAVASCRIPT: "main.js",
            SandboxLanguage.TYPESCRIPT: "main.ts",
            SandboxLanguage.JAVA: "Main.java",
            SandboxLanguage.GO: "main.go",
            SandboxLanguage.RUST: "main.rs",
            SandboxLanguage.CPP: "main.cpp",
            SandboxLanguage.RUBY: "main.rb",
            SandboxLanguage.PHP: "main.php",
        }
        return extensions.get(language, "main.txt")
    
    def _get_execution_command(self, language: SandboxLanguage, filename: str) -> str:
        """Get execution command for language"""
        commands = {
            SandboxLanguage.PYTHON: f"python {filename}",
            SandboxLanguage.JAVASCRIPT: f"node {filename}",
            SandboxLanguage.TYPESCRIPT: f"npx ts-node {filename}",
            SandboxLanguage.JAVA: f"javac {filename} && java Main",
            SandboxLanguage.GO: f"go run {filename}",
            SandboxLanguage.RUST: f"rustc {filename} && ./main",
            SandboxLanguage.CPP: f"g++ {filename} -o main && ./main",
            SandboxLanguage.RUBY: f"ruby {filename}",
            SandboxLanguage.PHP: f"php {filename}",
        }
        return commands.get(language, f"cat {filename}")
    
    def _calculate_cpu_usage(self, stats: Dict) -> Optional[float]:
        """Calculate CPU usage percentage from stats"""
        try:
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            
            if system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * 100.0
                return round(cpu_percent, 2)
        except (KeyError, ZeroDivisionError):
            pass
        
        return None


# Global sandbox manager instance
_sandbox_manager: Optional[SandboxManager] = None


def get_sandbox_manager() -> SandboxManager:
    """Get or create global sandbox manager instance"""
    global _sandbox_manager
    if _sandbox_manager is None:
        _sandbox_manager = SandboxManager()
    return _sandbox_manager