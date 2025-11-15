"""
VM Pool Manager
Manages concurrent virtual machines using Docker
"""

from typing import Dict, Any, List, Optional
import logging
import asyncio
import uuid
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class VMPoolManager:
    """
    Manages pool of virtual machines for concurrent execution
    """
    
    def __init__(self, max_vms_per_user: int = 10, max_total_vms: int = 100):
        self.max_vms_per_user = max_vms_per_user
        self.max_total_vms = max_total_vms
        self.active_vms: Dict[str, Any] = {}
        self.user_vm_count: Dict[int, int] = {}
        
        # Resource limits
        self.default_cpu_limit = 1.0  # CPU cores
        self.default_memory_limit = 512  # MB
        self.default_disk_limit = 1024  # MB
        self.default_timeout = 300  # seconds
        
        # Language configurations
        self.language_images = {
            'python': 'python:3.11-slim',
            'nodejs': 'node:20-slim',
            'java': 'openjdk:17-slim',
            'go': 'golang:1.21-alpine',
            'rust': 'rust:1.75-slim',
            'ruby': 'ruby:3.2-slim',
            'php': 'php:8.2-cli',
            'dotnet': 'mcr.microsoft.com/dotnet/sdk:8.0'
        }
        
        # Initialize Docker client
        self.docker_client = None
        self._init_docker()
    
    def _init_docker(self):
        """Initialize Docker client"""
        try:
            import docker
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.warning(f"Docker not available: {str(e)}")
            self.docker_client = None
    
    async def create_vm(
        self,
        user_id: int,
        name: str,
        language: str,
        cpu_limit: Optional[float] = None,
        memory_limit: Optional[int] = None,
        disk_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create new virtual machine
        
        Args:
            user_id: User ID
            name: VM name
            language: Programming language
            cpu_limit: CPU limit in cores
            memory_limit: Memory limit in MB
            disk_limit: Disk limit in MB
            
        Returns:
            VM details
        """
        try:
            # Check user's VM count
            user_vms = self.user_vm_count.get(user_id, 0)
            if user_vms >= self.max_vms_per_user:
                raise ValueError(f"Maximum VMs per user ({self.max_vms_per_user}) reached")
            
            # Check total VM count
            if len(self.active_vms) >= self.max_total_vms:
                raise ValueError(f"Maximum total VMs ({self.max_total_vms}) reached")
            
            # Validate language
            if language not in self.language_images:
                raise ValueError(f"Unsupported language: {language}")
            
            # Generate VM ID
            vm_id = f"vm_{uuid.uuid4().hex[:12]}"
            
            # Set resource limits
            cpu = cpu_limit or self.default_cpu_limit
            memory = memory_limit or self.default_memory_limit
            disk = disk_limit or self.default_disk_limit
            
            # Create container if Docker is available
            container_id = None
            if self.docker_client:
                container_id = await self._create_docker_container(
                    vm_id=vm_id,
                    language=language,
                    cpu_limit=cpu,
                    memory_limit=memory
                )
            
            # Store VM info
            vm_info = {
                "id": vm_id,
                "user_id": user_id,
                "name": name,
                "language": language,
                "status": "running",
                "cpu_limit": cpu,
                "memory_limit": memory,
                "disk_limit": disk,
                "container_id": container_id,
                "created_at": datetime.utcnow().isoformat(),
                "started_at": datetime.utcnow().isoformat(),
                "executions": []
            }
            
            self.active_vms[vm_id] = vm_info
            self.user_vm_count[user_id] = user_vms + 1
            
            logger.info(f"Created VM {vm_id} for user {user_id}")
            return vm_info
            
        except Exception as e:
            logger.error(f"Error creating VM: {str(e)}")
            raise
    
    async def _create_docker_container(
        self,
        vm_id: str,
        language: str,
        cpu_limit: float,
        memory_limit: int
    ) -> str:
        """Create Docker container for VM"""
        try:
            image = self.language_images[language]
            
            # Pull image if not exists
            try:
                self.docker_client.images.get(image)
            except:
                logger.info(f"Pulling image {image}...")
                self.docker_client.images.pull(image)
            
            # Create container
            container = self.docker_client.containers.run(
                image=image,
                name=vm_id,
                detach=True,
                remove=False,
                cpu_quota=int(cpu_limit * 100000),
                mem_limit=f"{memory_limit}m",
                network_mode='bridge',
                command='tail -f /dev/null'  # Keep container running
            )
            
            logger.info(f"Created Docker container {container.id} for VM {vm_id}")
            return container.id
            
        except Exception as e:
            logger.error(f"Error creating Docker container: {str(e)}")
            raise
    
    async def delete_vm(self, vm_id: str) -> bool:
        """
        Delete virtual machine
        
        Args:
            vm_id: VM ID
            
        Returns:
            Success status
        """
        try:
            if vm_id not in self.active_vms:
                raise ValueError(f"VM {vm_id} not found")
            
            vm_info = self.active_vms[vm_id]
            
            # Stop and remove Docker container
            if self.docker_client and vm_info.get('container_id'):
                await self._remove_docker_container(vm_info['container_id'])
            
            # Update counts
            user_id = vm_info['user_id']
            if user_id in self.user_vm_count:
                self.user_vm_count[user_id] -= 1
                if self.user_vm_count[user_id] <= 0:
                    del self.user_vm_count[user_id]
            
            # Remove from active VMs
            del self.active_vms[vm_id]
            
            logger.info(f"Deleted VM {vm_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting VM: {str(e)}")
            raise
    
    async def _remove_docker_container(self, container_id: str):
        """Remove Docker container"""
        try:
            container = self.docker_client.containers.get(container_id)
            container.stop(timeout=5)
            container.remove()
            logger.info(f"Removed Docker container {container_id}")
        except Exception as e:
            logger.warning(f"Error removing container {container_id}: {str(e)}")
    
    async def start_vm(self, vm_id: str) -> bool:
        """
        Start virtual machine
        
        Args:
            vm_id: VM ID
            
        Returns:
            Success status
        """
        try:
            if vm_id not in self.active_vms:
                raise ValueError(f"VM {vm_id} not found")
            
            vm_info = self.active_vms[vm_id]
            
            # Start Docker container
            if self.docker_client and vm_info.get('container_id'):
                container = self.docker_client.containers.get(vm_info['container_id'])
                container.start()
            
            vm_info['status'] = 'running'
            vm_info['started_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Started VM {vm_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting VM: {str(e)}")
            raise
    
    async def stop_vm(self, vm_id: str) -> bool:
        """
        Stop virtual machine
        
        Args:
            vm_id: VM ID
            
        Returns:
            Success status
        """
        try:
            if vm_id not in self.active_vms:
                raise ValueError(f"VM {vm_id} not found")
            
            vm_info = self.active_vms[vm_id]
            
            # Stop Docker container
            if self.docker_client and vm_info.get('container_id'):
                container = self.docker_client.containers.get(vm_info['container_id'])
                container.stop(timeout=5)
            
            vm_info['status'] = 'stopped'
            vm_info['stopped_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Stopped VM {vm_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping VM: {str(e)}")
            raise
    
    async def restart_vm(self, vm_id: str) -> bool:
        """
        Restart virtual machine
        
        Args:
            vm_id: VM ID
            
        Returns:
            Success status
        """
        try:
            await self.stop_vm(vm_id)
            await asyncio.sleep(1)
            await self.start_vm(vm_id)
            return True
        except Exception as e:
            logger.error(f"Error restarting VM: {str(e)}")
            raise
    
    async def execute_in_vm(
        self,
        vm_id: str,
        code: str,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute code in virtual machine
        
        Args:
            vm_id: VM ID
            code: Code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result
        """
        try:
            if vm_id not in self.active_vms:
                raise ValueError(f"VM {vm_id} not found")
            
            vm_info = self.active_vms[vm_id]
            
            if vm_info['status'] != 'running':
                raise ValueError(f"VM {vm_id} is not running")
            
            timeout = timeout or self.default_timeout
            start_time = datetime.utcnow()
            
            # Execute in Docker container
            if self.docker_client and vm_info.get('container_id'):
                result = await self._execute_in_docker(
                    container_id=vm_info['container_id'],
                    language=vm_info['language'],
                    code=code,
                    timeout=timeout
                )
            else:
                # Fallback to local execution (for testing)
                result = await self._execute_locally(
                    language=vm_info['language'],
                    code=code,
                    timeout=timeout
                )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            execution_result = {
                "vm_id": vm_id,
                "output": result.get('output', ''),
                "error": result.get('error', ''),
                "exit_code": result.get('exit_code', 0),
                "execution_time": execution_time,
                "executed_at": start_time.isoformat()
            }
            
            # Store execution history
            vm_info['executions'].append(execution_result)
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing in VM: {str(e)}")
            raise
    
    async def _execute_in_docker(
        self,
        container_id: str,
        language: str,
        code: str,
        timeout: int
    ) -> Dict[str, Any]:
        """Execute code in Docker container"""
        try:
            container = self.docker_client.containers.get(container_id)
            
            # Prepare execution command based on language
            if language == 'python':
                cmd = f"python -c '{code}'"
            elif language == 'nodejs':
                cmd = f"node -e '{code}'"
            elif language == 'java':
                # Save to file and compile/run
                cmd = f"echo '{code}' > Main.java && javac Main.java && java Main"
            elif language == 'go':
                cmd = f"echo '{code}' > main.go && go run main.go"
            elif language == 'rust':
                cmd = f"echo '{code}' > main.rs && rustc main.rs && ./main"
            elif language == 'ruby':
                cmd = f"ruby -e '{code}'"
            elif language == 'php':
                cmd = f"php -r '{code}'"
            else:
                cmd = code
            
            # Execute command
            exec_result = container.exec_run(
                cmd=f"/bin/sh -c &quot;{cmd}&quot;",
                demux=True
            )
            
            stdout = exec_result.output[0].decode('utf-8') if exec_result.output[0] else ''
            stderr = exec_result.output[1].decode('utf-8') if exec_result.output[1] else ''
            
            return {
                'output': stdout,
                'error': stderr,
                'exit_code': exec_result.exit_code
            }
            
        except Exception as e:
            return {
                'output': '',
                'error': str(e),
                'exit_code': 1
            }
    
    async def _execute_locally(
        self,
        language: str,
        code: str,
        timeout: int
    ) -> Dict[str, Any]:
        """Execute code locally (fallback)"""
        try:
            import subprocess
            
            if language == 'python':
                cmd = ['python', '-c', code]
            elif language == 'nodejs':
                cmd = ['node', '-e', code]
            else:
                raise ValueError(f"Local execution not supported for {language}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                'output': result.stdout,
                'error': result.stderr,
                'exit_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'output': '',
                'error': 'Execution timeout',
                'exit_code': 124
            }
        except Exception as e:
            return {
                'output': '',
                'error': str(e),
                'exit_code': 1
            }
    
    async def get_vm_status(self, vm_id: str) -> Dict[str, Any]:
        """
        Get VM status
        
        Args:
            vm_id: VM ID
            
        Returns:
            VM status information
        """
        try:
            if vm_id not in self.active_vms:
                raise ValueError(f"VM {vm_id} not found")
            
            vm_info = self.active_vms[vm_id]
            
            # Get container stats if available
            stats = {}
            if self.docker_client and vm_info.get('container_id'):
                try:
                    container = self.docker_client.containers.get(vm_info['container_id'])
                    container_stats = container.stats(stream=False)
                    
                    # Calculate CPU and memory usage
                    cpu_delta = container_stats['cpu_stats']['cpu_usage']['total_usage'] - \
                               container_stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = container_stats['cpu_stats']['system_cpu_usage'] - \
                                  container_stats['precpu_stats']['system_cpu_usage']
                    cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0
                    
                    memory_usage = container_stats['memory_stats']['usage']
                    memory_limit = container_stats['memory_stats']['limit']
                    memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0
                    
                    stats = {
                        'cpu_percent': round(cpu_percent, 2),
                        'memory_usage_mb': round(memory_usage / (1024 * 1024), 2),
                        'memory_percent': round(memory_percent, 2)
                    }
                except:
                    pass
            
            return {
                **vm_info,
                'stats': stats,
                'execution_count': len(vm_info.get('executions', []))
            }
            
        except Exception as e:
            logger.error(f"Error getting VM status: {str(e)}")
            raise
    
    async def get_vm_logs(self, vm_id: str, tail: int = 100) -> str:
        """
        Get VM logs
        
        Args:
            vm_id: VM ID
            tail: Number of lines to return
            
        Returns:
            Log content
        """
        try:
            if vm_id not in self.active_vms:
                raise ValueError(f"VM {vm_id} not found")
            
            vm_info = self.active_vms[vm_id]
            
            if self.docker_client and vm_info.get('container_id'):
                container = self.docker_client.containers.get(vm_info['container_id'])
                logs = container.logs(tail=tail).decode('utf-8')
                return logs
            
            return "No logs available"
            
        except Exception as e:
            logger.error(f"Error getting VM logs: {str(e)}")
            raise
    
    async def list_vms(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all VMs
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of VMs
        """
        try:
            vms = list(self.active_vms.values())
            
            if user_id is not None:
                vms = [vm for vm in vms if vm['user_id'] == user_id]
            
            return vms
            
        except Exception as e:
            logger.error(f"Error listing VMs: {str(e)}")
            raise
    
    async def batch_execute(
        self,
        vm_ids: List[str],
        code: str,
        timeout: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute code in multiple VMs concurrently
        
        Args:
            vm_ids: List of VM IDs
            code: Code to execute
            timeout: Execution timeout
            
        Returns:
            List of execution results
        """
        try:
            tasks = [
                self.execute_in_vm(vm_id, code, timeout)
                for vm_id in vm_ids
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to error results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'vm_id': vm_ids[i],
                        'output': '',
                        'error': str(result),
                        'exit_code': 1,
                        'execution_time': 0,
                        'executed_at': datetime.utcnow().isoformat()
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch execution: {str(e)}")
            raise
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """
        Get pool status
        
        Returns:
            Pool status information
        """
        try:
            total_vms = len(self.active_vms)
            running_vms = sum(1 for vm in self.active_vms.values() if vm['status'] == 'running')
            stopped_vms = sum(1 for vm in self.active_vms.values() if vm['status'] == 'stopped')
            
            return {
                'total_vms': total_vms,
                'running_vms': running_vms,
                'stopped_vms': stopped_vms,
                'max_vms_per_user': self.max_vms_per_user,
                'max_total_vms': self.max_total_vms,
                'available_slots': self.max_total_vms - total_vms,
                'users_with_vms': len(self.user_vm_count),
                'docker_available': self.docker_client is not None
            }
            
        except Exception as e:
            logger.error(f"Error getting pool status: {str(e)}")
            raise
    
    async def cleanup_inactive_vms(self, max_age_hours: int = 24):
        """
        Clean up inactive VMs
        
        Args:
            max_age_hours: Maximum age in hours
        """
        try:
            from datetime import timedelta
            
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            vms_to_delete = []
            for vm_id, vm_info in self.active_vms.items():
                created_at = datetime.fromisoformat(vm_info['created_at'])
                if created_at < cutoff_time and vm_info['status'] == 'stopped':
                    vms_to_delete.append(vm_id)
            
            for vm_id in vms_to_delete:
                await self.delete_vm(vm_id)
                logger.info(f"Cleaned up inactive VM {vm_id}")
            
            return len(vms_to_delete)
            
        except Exception as e:
            logger.error(f"Error cleaning up VMs: {str(e)}")
            raise