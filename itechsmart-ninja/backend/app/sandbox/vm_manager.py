"""
VM/Sandbox Manager - Manages Docker containers for code execution
"""
import docker
import asyncio
import logging
import tempfile
import os
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SandboxEnvironment:
    """Represents a sandbox execution environment"""
    
    def __init__(self, container_id: str, language: str, user_id: int):
        self.container_id = container_id
        self.language = language
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.last_used = datetime.utcnow()
        self.execution_count = 0
        self.status = "running"
    
    def update_usage(self):
        """Update usage statistics"""
        self.last_used = datetime.utcnow()
        self.execution_count += 1
    
    def is_expired(self, max_age_minutes: int = 30) -> bool:
        """Check if sandbox has expired"""
        age = datetime.utcnow() - self.last_used
        return age > timedelta(minutes=max_age_minutes)


class VMManager:
    """Manages virtual machines/containers for code execution"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.sandboxes: Dict[str, SandboxEnvironment] = {}
            self.max_sandboxes = 10
            self.max_sandbox_age_minutes = 30
            
            logger.info("VMManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            self.client = None
    
    async def create_sandbox(
        self,
        language: str,
        user_id: int,
        memory_limit: str = "512m",
        cpu_limit: float = 1.0
    ) -> Optional[str]:
        """Create a new sandbox environment"""
        try:
            if not self.client:
                raise Exception("Docker client not available")
            
            # Clean up expired sandboxes
            await self._cleanup_expired_sandboxes()
            
            # Check sandbox limit
            if len(self.sandboxes) >= self.max_sandboxes:
                await self._cleanup_oldest_sandbox()
            
            # Select appropriate image
            image = self._get_image_for_language(language)
            
            # Create container
            container = self.client.containers.run(
                image,
                detach=True,
                mem_limit=memory_limit,
                cpu_quota=int(cpu_limit * 100000),
                network_disabled=False,  # Enable for package installation
                remove=False,
                tty=True,
                stdin_open=True
            )
            
            sandbox = SandboxEnvironment(container.id, language, user_id)
            self.sandboxes[container.id] = sandbox
            
            logger.info(f"Created sandbox {container.id} for user {user_id}")
            return container.id
            
        except Exception as e:
            logger.error(f"Failed to create sandbox: {str(e)}")
            return None
    
    async def execute_code(
        self,
        sandbox_id: str,
        code: str,
        language: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Execute code in a sandbox"""
        try:
            if not self.client:
                raise Exception("Docker client not available")
            
            sandbox = self.sandboxes.get(sandbox_id)
            if not sandbox:
                raise Exception(f"Sandbox {sandbox_id} not found")
            
            # Get container
            container = self.client.containers.get(sandbox_id)
            
            # Prepare code file
            code_file = self._prepare_code_file(code, language)
            
            # Copy code to container
            await self._copy_to_container(container, code_file, f"/tmp/code.{self._get_extension(language)}")
            
            # Execute code
            exec_command = self._get_exec_command(language)
            result = container.exec_run(
                exec_command,
                demux=True,
                workdir="/tmp"
            )
            
            # Update sandbox usage
            sandbox.update_usage()
            
            # Parse result
            stdout = result.output[0].decode() if result.output[0] else ""
            stderr = result.output[1].decode() if result.output[1] else ""
            
            # Clean up
            os.unlink(code_file)
            
            return {
                "success": result.exit_code == 0,
                "exit_code": result.exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "sandbox_id": sandbox_id
            }
            
        except Exception as e:
            logger.error(f"Code execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sandbox_id": sandbox_id
            }
    
    async def install_package(
        self,
        sandbox_id: str,
        package: str,
        language: str
    ) -> Dict[str, Any]:
        """Install a package in the sandbox"""
        try:
            if not self.client:
                raise Exception("Docker client not available")
            
            container = self.client.containers.get(sandbox_id)
            
            # Get install command
            install_cmd = self._get_install_command(language, package)
            
            # Execute install
            result = container.exec_run(install_cmd, demux=True)
            
            stdout = result.output[0].decode() if result.output[0] else ""
            stderr = result.output[1].decode() if result.output[1] else ""
            
            return {
                "success": result.exit_code == 0,
                "stdout": stdout,
                "stderr": stderr
            }
            
        except Exception as e:
            logger.error(f"Package installation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def destroy_sandbox(self, sandbox_id: str) -> bool:
        """Destroy a sandbox environment"""
        try:
            if not self.client:
                return False
            
            container = self.client.containers.get(sandbox_id)
            container.stop(timeout=5)
            container.remove()
            
            if sandbox_id in self.sandboxes:
                del self.sandboxes[sandbox_id]
            
            logger.info(f"Destroyed sandbox {sandbox_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy sandbox: {str(e)}")
            return False
    
    async def get_sandbox_info(self, sandbox_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a sandbox"""
        try:
            sandbox = self.sandboxes.get(sandbox_id)
            if not sandbox:
                return None
            
            container = self.client.containers.get(sandbox_id)
            stats = container.stats(stream=False)
            
            return {
                "sandbox_id": sandbox_id,
                "language": sandbox.language,
                "user_id": sandbox.user_id,
                "status": sandbox.status,
                "created_at": sandbox.created_at.isoformat(),
                "last_used": sandbox.last_used.isoformat(),
                "execution_count": sandbox.execution_count,
                "memory_usage": stats.get("memory_stats", {}).get("usage", 0),
                "cpu_usage": stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get sandbox info: {str(e)}")
            return None
    
    async def list_sandboxes(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all sandboxes, optionally filtered by user"""
        sandboxes = []
        
        for sandbox_id, sandbox in self.sandboxes.items():
            if user_id is None or sandbox.user_id == user_id:
                info = await self.get_sandbox_info(sandbox_id)
                if info:
                    sandboxes.append(info)
        
        return sandboxes
    
    async def cleanup_all(self):
        """Clean up all sandboxes"""
        sandbox_ids = list(self.sandboxes.keys())
        for sandbox_id in sandbox_ids:
            await self.destroy_sandbox(sandbox_id)
    
    # Helper methods
    
    def _get_image_for_language(self, language: str) -> str:
        """Get Docker image for language"""
        images = {
            "python": "python:3.11-slim",
            "javascript": "node:20-slim",
            "typescript": "node:20-slim",
            "java": "openjdk:17-slim",
            "go": "golang:1.21-alpine",
            "rust": "rust:1.75-slim",
            "ruby": "ruby:3.2-slim",
            "php": "php:8.2-cli",
        }
        return images.get(language.lower(), "python:3.11-slim")
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "go": "go",
            "rust": "rs",
            "ruby": "rb",
            "php": "php",
        }
        return extensions.get(language.lower(), "txt")
    
    def _get_exec_command(self, language: str) -> str:
        """Get execution command for language"""
        commands = {
            "python": "python /tmp/code.py",
            "javascript": "node /tmp/code.js",
            "typescript": "ts-node /tmp/code.ts",
            "java": "javac /tmp/code.java && java -cp /tmp code",
            "go": "go run /tmp/code.go",
            "rust": "rustc /tmp/code.rs -o /tmp/code && /tmp/code",
            "ruby": "ruby /tmp/code.rb",
            "php": "php /tmp/code.php",
        }
        return commands.get(language.lower(), "cat /tmp/code.txt")
    
    def _get_install_command(self, language: str, package: str) -> str:
        """Get package install command"""
        commands = {
            "python": f"pip install {package}",
            "javascript": f"npm install {package}",
            "typescript": f"npm install {package}",
            "ruby": f"gem install {package}",
            "php": f"composer require {package}",
        }
        return commands.get(language.lower(), f"echo 'Package installation not supported for {language}'")
    
    def _prepare_code_file(self, code: str, language: str) -> str:
        """Prepare code file for execution"""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'.{self._get_extension(language)}',
            delete=False
        ) as f:
            f.write(code)
            return f.name
    
    async def _copy_to_container(self, container, src_path: str, dest_path: str):
        """Copy file to container"""
        try:
            with open(src_path, 'rb') as f:
                data = f.read()
            
            # Create tar archive
            import tarfile
            import io
            
            tar_stream = io.BytesIO()
            tar = tarfile.open(fileobj=tar_stream, mode='w')
            
            tarinfo = tarfile.TarInfo(name=os.path.basename(dest_path))
            tarinfo.size = len(data)
            tar.addfile(tarinfo, io.BytesIO(data))
            tar.close()
            
            tar_stream.seek(0)
            container.put_archive(os.path.dirname(dest_path), tar_stream)
            
        except Exception as e:
            logger.error(f"Failed to copy file to container: {str(e)}")
            raise
    
    async def _cleanup_expired_sandboxes(self):
        """Clean up expired sandboxes"""
        expired = [
            sandbox_id
            for sandbox_id, sandbox in self.sandboxes.items()
            if sandbox.is_expired(self.max_sandbox_age_minutes)
        ]
        
        for sandbox_id in expired:
            await self.destroy_sandbox(sandbox_id)
    
    async def _cleanup_oldest_sandbox(self):
        """Clean up the oldest sandbox"""
        if not self.sandboxes:
            return
        
        oldest_id = min(
            self.sandboxes.keys(),
            key=lambda k: self.sandboxes[k].created_at
        )
        await self.destroy_sandbox(oldest_id)


# Global VM manager instance
vm_manager = VMManager()