"""
Virtual Machine Manager for iTechSmart Ninja
Provides dedicated VM provisioning and management using cloud providers
"""

import asyncio
import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)


class VMStatus(str, Enum):
    """VM lifecycle states"""
    PROVISIONING = "provisioning"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    REBOOTING = "rebooting"
    TERMINATED = "terminated"
    ERROR = "error"


class VMProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    DIGITALOCEAN = "digitalocean"
    LINODE = "linode"
    LOCAL = "local"  # Local VMs using libvirt/KVM


class VMSize(str, Enum):
    """Standard VM sizes"""
    MICRO = "micro"      # 1 vCPU, 1GB RAM
    SMALL = "small"      # 1 vCPU, 2GB RAM
    MEDIUM = "medium"    # 2 vCPU, 4GB RAM
    LARGE = "large"      # 4 vCPU, 8GB RAM
    XLARGE = "xlarge"    # 8 vCPU, 16GB RAM
    XXLARGE = "xxlarge"  # 16 vCPU, 32GB RAM


class VMImage(str, Enum):
    """Standard VM images"""
    UBUNTU_22_04 = "ubuntu-22.04"
    UBUNTU_20_04 = "ubuntu-20.04"
    DEBIAN_11 = "debian-11"
    CENTOS_8 = "centos-8"
    FEDORA_38 = "fedora-38"
    WINDOWS_SERVER_2022 = "windows-server-2022"
    WINDOWS_SERVER_2019 = "windows-server-2019"


@dataclass
class VMConfig:
    """Configuration for VM provisioning"""
    provider: VMProvider
    size: VMSize
    image: VMImage
    region: str = "us-east-1"
    disk_size_gb: int = 50
    enable_public_ip: bool = True
    enable_monitoring: bool = True
    ssh_keys: List[str] = None
    tags: Dict[str, str] = None
    user_data: Optional[str] = None  # Cloud-init script
    
    def __post_init__(self):
        if self.ssh_keys is None:
            self.ssh_keys = []
        if self.tags is None:
            self.tags = {}


@dataclass
class VMInfo:
    """Information about a VM instance"""
    vm_id: str
    name: str
    provider: VMProvider
    status: VMStatus
    size: VMSize
    image: VMImage
    region: str
    public_ip: Optional[str]
    private_ip: Optional[str]
    provider_vm_id: Optional[str]  # Provider-specific VM ID
    created_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]
    config: VMConfig
    metadata: Dict[str, Any]
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
class VMMetrics:
    """VM performance metrics"""
    vm_id: str
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_in_bytes: int
    network_out_bytes: int
    disk_read_bytes: int
    disk_write_bytes: int


class BaseVMProvider:
    """Base class for VM providers"""
    
    async def provision_vm(self, config: VMConfig, name: str) -> Dict[str, Any]:
        """Provision a new VM"""
        raise NotImplementedError
    
    async def start_vm(self, provider_vm_id: str) -> bool:
        """Start a VM"""
        raise NotImplementedError
    
    async def stop_vm(self, provider_vm_id: str) -> bool:
        """Stop a VM"""
        raise NotImplementedError
    
    async def reboot_vm(self, provider_vm_id: str) -> bool:
        """Reboot a VM"""
        raise NotImplementedError
    
    async def terminate_vm(self, provider_vm_id: str) -> bool:
        """Terminate a VM"""
        raise NotImplementedError
    
    async def get_vm_status(self, provider_vm_id: str) -> VMStatus:
        """Get VM status"""
        raise NotImplementedError
    
    async def get_vm_metrics(self, provider_vm_id: str) -> VMMetrics:
        """Get VM metrics"""
        raise NotImplementedError


class LocalVMProvider(BaseVMProvider):
    """Local VM provider using Docker (simulated VMs)"""
    
    def __init__(self):
        """Initialize local provider"""
        try:
            import docker
            self.client = docker.from_env()
            self.containers: Dict[str, Any] = {}
            logger.info("LocalVMProvider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
    
    async def provision_vm(self, config: VMConfig, name: str) -> Dict[str, Any]:
        """Provision a new VM using Docker"""
        try:
            # Map VM image to Docker image
            image_map = {
                VMImage.UBUNTU_22_04: "ubuntu:22.04",
                VMImage.UBUNTU_20_04: "ubuntu:20.04",
                VMImage.DEBIAN_11: "debian:11",
                VMImage.CENTOS_8: "centos:8",
                VMImage.FEDORA_38: "fedora:38",
            }
            
            docker_image = image_map.get(config.image, "ubuntu:22.04")
            
            # Pull image if not available
            try:
                self.client.images.get(docker_image)
            except:
                logger.info(f"Pulling Docker image: {docker_image}")
                self.client.images.pull(docker_image)
            
            # Map VM size to container resources
            size_map = {
                VMSize.MICRO: {"mem_limit": "1g", "nano_cpus": 1000000000},
                VMSize.SMALL: {"mem_limit": "2g", "nano_cpus": 1000000000},
                VMSize.MEDIUM: {"mem_limit": "4g", "nano_cpus": 2000000000},
                VMSize.LARGE: {"mem_limit": "8g", "nano_cpus": 4000000000},
                VMSize.XLARGE: {"mem_limit": "16g", "nano_cpus": 8000000000},
                VMSize.XXLARGE: {"mem_limit": "32g", "nano_cpus": 16000000000},
            }
            
            resources = size_map.get(config.size, size_map[VMSize.SMALL])
            
            # Create container
            container = self.client.containers.create(
                image=docker_image,
                name=f"vm-{name}",
                detach=True,
                mem_limit=resources["mem_limit"],
                nano_cpus=resources["nano_cpus"],
                command="tail -f /dev/null",
                labels={
                    "vm_name": name,
                    "vm_size": config.size.value,
                    "vm_image": config.image.value,
                    "managed_by": "itechsmart-ninja"
                }
            )
            
            # Start container
            container.start()
            
            # Get container info
            container.reload()
            
            # Store container reference
            self.containers[container.id] = container
            
            return {
                "provider_vm_id": container.id,
                "public_ip": None,  # Local VMs don't have public IPs
                "private_ip": container.attrs['NetworkSettings']['IPAddress'],
                "status": VMStatus.RUNNING
            }
            
        except Exception as e:
            logger.error(f"Failed to provision VM: {e}")
            raise
    
    async def start_vm(self, provider_vm_id: str) -> bool:
        """Start a VM"""
        try:
            container = self.client.containers.get(provider_vm_id)
            container.start()
            return True
        except Exception as e:
            logger.error(f"Failed to start VM {provider_vm_id}: {e}")
            raise
    
    async def stop_vm(self, provider_vm_id: str) -> bool:
        """Stop a VM"""
        try:
            container = self.client.containers.get(provider_vm_id)
            container.stop(timeout=30)
            return True
        except Exception as e:
            logger.error(f"Failed to stop VM {provider_vm_id}: {e}")
            raise
    
    async def reboot_vm(self, provider_vm_id: str) -> bool:
        """Reboot a VM"""
        try:
            container = self.client.containers.get(provider_vm_id)
            container.restart(timeout=30)
            return True
        except Exception as e:
            logger.error(f"Failed to reboot VM {provider_vm_id}: {e}")
            raise
    
    async def terminate_vm(self, provider_vm_id: str) -> bool:
        """Terminate a VM"""
        try:
            container = self.client.containers.get(provider_vm_id)
            container.stop(timeout=10)
            container.remove(force=True)
            
            if provider_vm_id in self.containers:
                del self.containers[provider_vm_id]
            
            return True
        except Exception as e:
            logger.error(f"Failed to terminate VM {provider_vm_id}: {e}")
            raise
    
    async def get_vm_status(self, provider_vm_id: str) -> VMStatus:
        """Get VM status"""
        try:
            container = self.client.containers.get(provider_vm_id)
            status = container.status
            
            status_map = {
                "running": VMStatus.RUNNING,
                "exited": VMStatus.STOPPED,
                "paused": VMStatus.STOPPED,
                "restarting": VMStatus.REBOOTING,
                "created": VMStatus.PROVISIONING,
            }
            
            return status_map.get(status, VMStatus.ERROR)
        except Exception as e:
            logger.error(f"Failed to get VM status {provider_vm_id}: {e}")
            return VMStatus.ERROR
    
    async def get_vm_metrics(self, provider_vm_id: str) -> VMMetrics:
        """Get VM metrics"""
        try:
            container = self.client.containers.get(provider_vm_id)
            stats = container.stats(stream=False)
            
            # Calculate CPU usage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Calculate memory usage
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 1)
            memory_percent = (memory_usage / memory_limit) * 100.0
            
            # Network stats
            networks = stats.get('networks', {})
            network_in = sum(net.get('rx_bytes', 0) for net in networks.values())
            network_out = sum(net.get('tx_bytes', 0) for net in networks.values())
            
            return VMMetrics(
                vm_id=provider_vm_id,
                timestamp=datetime.now(),
                cpu_usage_percent=round(cpu_percent, 2),
                memory_usage_percent=round(memory_percent, 2),
                disk_usage_percent=0.0,  # Not available in Docker stats
                network_in_bytes=network_in,
                network_out_bytes=network_out,
                disk_read_bytes=0,
                disk_write_bytes=0
            )
        except Exception as e:
            logger.error(f"Failed to get VM metrics {provider_vm_id}: {e}")
            raise


class VMManager:
    """Manages virtual machine lifecycle"""
    
    def __init__(self):
        """Initialize VM manager"""
        self.vms: Dict[str, VMInfo] = {}
        self.providers: Dict[VMProvider, BaseVMProvider] = {
            VMProvider.LOCAL: LocalVMProvider()
        }
        logger.info("VMManager initialized successfully")
    
    async def create_vm(
        self,
        name: str,
        config: VMConfig
    ) -> VMInfo:
        """
        Create a new virtual machine
        
        Args:
            name: Name for the VM
            config: VM configuration
            
        Returns:
            VMInfo object with VM details
        """
        vm_id = str(uuid.uuid4())
        
        vm_info = VMInfo(
            vm_id=vm_id,
            name=name,
            provider=config.provider,
            status=VMStatus.PROVISIONING,
            size=config.size,
            image=config.image,
            region=config.region,
            public_ip=None,
            private_ip=None,
            provider_vm_id=None,
            created_at=datetime.now(),
            started_at=None,
            stopped_at=None,
            config=config,
            metadata={}
        )
        
        self.vms[vm_id] = vm_info
        
        try:
            # Get provider
            provider = self.providers.get(config.provider)
            if not provider:
                raise ValueError(f"Unsupported provider: {config.provider}")
            
            # Provision VM
            result = await provider.provision_vm(config, name)
            
            # Update VM info
            vm_info.provider_vm_id = result["provider_vm_id"]
            vm_info.public_ip = result.get("public_ip")
            vm_info.private_ip = result.get("private_ip")
            vm_info.status = result.get("status", VMStatus.RUNNING)
            vm_info.started_at = datetime.now()
            
            logger.info(f"VM {vm_id} created successfully")
            return vm_info
            
        except Exception as e:
            logger.error(f"Failed to create VM {vm_id}: {e}")
            vm_info.status = VMStatus.ERROR
            vm_info.error_message = str(e)
            raise
    
    async def start_vm(self, vm_id: str) -> bool:
        """Start a VM"""
        vm_info = self.vms.get(vm_id)
        if not vm_info:
            raise ValueError(f"VM {vm_id} not found")
        
        if vm_info.status != VMStatus.STOPPED:
            raise ValueError(f"VM {vm_id} is not stopped (status: {vm_info.status})")
        
        try:
            vm_info.status = VMStatus.STARTING
            
            provider = self.providers.get(vm_info.provider)
            await provider.start_vm(vm_info.provider_vm_id)
            
            vm_info.status = VMStatus.RUNNING
            vm_info.started_at = datetime.now()
            
            logger.info(f"VM {vm_id} started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start VM {vm_id}: {e}")
            vm_info.status = VMStatus.ERROR
            vm_info.error_message = str(e)
            raise
    
    async def stop_vm(self, vm_id: str) -> bool:
        """Stop a VM"""
        vm_info = self.vms.get(vm_id)
        if not vm_info:
            raise ValueError(f"VM {vm_id} not found")
        
        if vm_info.status != VMStatus.RUNNING:
            raise ValueError(f"VM {vm_id} is not running (status: {vm_info.status})")
        
        try:
            vm_info.status = VMStatus.STOPPING
            
            provider = self.providers.get(vm_info.provider)
            await provider.stop_vm(vm_info.provider_vm_id)
            
            vm_info.status = VMStatus.STOPPED
            vm_info.stopped_at = datetime.now()
            
            logger.info(f"VM {vm_id} stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to stop VM {vm_id}: {e}")
            vm_info.status = VMStatus.ERROR
            vm_info.error_message = str(e)
            raise
    
    async def reboot_vm(self, vm_id: str) -> bool:
        """Reboot a VM"""
        vm_info = self.vms.get(vm_id)
        if not vm_info:
            raise ValueError(f"VM {vm_id} not found")
        
        try:
            vm_info.status = VMStatus.REBOOTING
            
            provider = self.providers.get(vm_info.provider)
            await provider.reboot_vm(vm_info.provider_vm_id)
            
            vm_info.status = VMStatus.RUNNING
            
            logger.info(f"VM {vm_id} rebooted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reboot VM {vm_id}: {e}")
            vm_info.status = VMStatus.ERROR
            vm_info.error_message = str(e)
            raise
    
    async def terminate_vm(self, vm_id: str) -> bool:
        """Terminate and remove a VM"""
        vm_info = self.vms.get(vm_id)
        if not vm_info:
            raise ValueError(f"VM {vm_id} not found")
        
        try:
            provider = self.providers.get(vm_info.provider)
            await provider.terminate_vm(vm_info.provider_vm_id)
            
            vm_info.status = VMStatus.TERMINATED
            vm_info.stopped_at = datetime.now()
            
            logger.info(f"VM {vm_id} terminated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to terminate VM {vm_id}: {e}")
            raise
    
    async def get_vm_info(self, vm_id: str) -> Optional[VMInfo]:
        """Get information about a VM"""
        return self.vms.get(vm_id)
    
    async def list_vms(
        self,
        status: Optional[VMStatus] = None,
        provider: Optional[VMProvider] = None
    ) -> List[VMInfo]:
        """List all VMs with optional filtering"""
        vms = list(self.vms.values())
        
        if status:
            vms = [v for v in vms if v.status == status]
        
        if provider:
            vms = [v for v in vms if v.provider == provider]
        
        return vms
    
    async def get_vm_metrics(self, vm_id: str) -> VMMetrics:
        """Get VM performance metrics"""
        vm_info = self.vms.get(vm_id)
        if not vm_info:
            raise ValueError(f"VM {vm_id} not found")
        
        provider = self.providers.get(vm_info.provider)
        return await provider.get_vm_metrics(vm_info.provider_vm_id)
    
    async def cleanup_terminated_vms(self, max_age_hours: int = 24) -> int:
        """Clean up terminated VMs older than specified age"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned = 0
        
        for vm_id, vm_info in list(self.vms.items()):
            if vm_info.status == VMStatus.TERMINATED and vm_info.stopped_at:
                if vm_info.stopped_at < cutoff_time:
                    del self.vms[vm_id]
                    cleaned += 1
        
        logger.info(f"Cleaned up {cleaned} terminated VMs")
        return cleaned


# Global VM manager instance
_vm_manager: Optional[VMManager] = None


def get_vm_manager() -> VMManager:
    """Get or create global VM manager instance"""
    global _vm_manager
    if _vm_manager is None:
        _vm_manager = VMManager()
    return _vm_manager