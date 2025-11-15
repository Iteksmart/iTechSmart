"""
Network Device Manager - CLI access to switches, routers, and network devices
Supports Cisco, Juniper, Arista, and other vendors
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from enum import Enum
import re

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
import paramiko

from core.models import ExecutionResult, Platform


class NetworkVendor(Enum):
    """Supported network device vendors"""
    CISCO_IOS = "cisco_ios"
    CISCO_XE = "cisco_xe"
    CISCO_NXOS = "cisco_nxos"
    CISCO_ASA = "cisco_asa"
    JUNIPER = "juniper"
    JUNIPER_JUNOS = "juniper_junos"
    ARISTA_EOS = "arista_eos"
    HP_PROCURVE = "hp_procurve"
    HP_COMWARE = "hp_comware"
    DELL_FORCE10 = "dell_force10"
    PALO_ALTO = "paloalto_panos"
    FORTINET = "fortinet"
    GENERIC = "generic_termserver"


class NetworkDeviceManager:
    """
    Manage network devices via CLI
    
    Features:
    - Multi-vendor support (Cisco, Juniper, Arista, etc.)
    - Configuration management
    - VLAN management
    - Routing configuration
    - Security policy management
    - Topology discovery
    - Automated troubleshooting
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_connections = {}
        self.device_inventory = {}
    
    async def connect_device(
        self,
        host: str,
        username: str,
        password: str,
        device_type: NetworkVendor,
        port: int = 22,
        enable_password: Optional[str] = None
    ) -> bool:
        """Connect to a network device"""
        
        device_key = f"{host}:{port}"
        
        try:
            self.logger.info(f"Connecting to {device_type.value} device at {host}:{port}")
            
            device_params = {
                'device_type': device_type.value,
                'host': host,
                'username': username,
                'password': password,
                'port': port,
                'timeout': 30,
                'session_timeout': 60,
                'auth_timeout': 30,
                'banner_timeout': 15,
            }
            
            if enable_password:
                device_params['secret'] = enable_password
            
            # Create connection
            connection = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ConnectHandler(**device_params)
            )
            
            # Enter enable mode if needed
            if enable_password and hasattr(connection, 'enable'):
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    connection.enable
                )
            
            self.active_connections[device_key] = {
                'connection': connection,
                'device_type': device_type,
                'host': host,
                'connected_at': asyncio.get_event_loop().time()
            }
            
            self.logger.info(f"✅ Connected to {host}")
            return True
            
        except NetmikoAuthenticationException as e:
            self.logger.error(f"Authentication failed for {host}: {e}")
            return False
        except NetmikoTimeoutException as e:
            self.logger.error(f"Connection timeout for {host}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to connect to {host}: {e}")
            return False
    
    async def execute_command(
        self,
        host: str,
        command: str,
        port: int = 22,
        config_mode: bool = False
    ) -> ExecutionResult:
        """Execute command on network device"""
        
        device_key = f"{host}:{port}"
        
        if device_key not in self.active_connections:
            return ExecutionResult(
                success=False,
                error=f"No active connection to {host}:{port}"
            )
        
        try:
            connection = self.active_connections[device_key]['connection']
            
            self.logger.info(f"Executing on {host}: {command}")
            
            if config_mode:
                # Configuration commands
                output = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: connection.send_config_set([command])
                )
            else:
                # Show commands
                output = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: connection.send_command(command)
                )
            
            return ExecutionResult(
                success=True,
                stdout=output,
                exit_code=0
            )
            
        except Exception as e:
            self.logger.error(f"Command execution failed on {host}: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                stderr=str(e)
            )
    
    async def configure_vlan(
        self,
        host: str,
        vlan_id: int,
        vlan_name: str,
        port: int = 22
    ) -> ExecutionResult:
        """Configure VLAN on switch"""
        
        device_key = f"{host}:{port}"
        
        if device_key not in self.active_connections:
            return ExecutionResult(
                success=False,
                error=f"No active connection to {host}"
            )
        
        device_type = self.active_connections[device_key]['device_type']
        
        # Generate commands based on vendor
        if device_type in [NetworkVendor.CISCO_IOS, NetworkVendor.CISCO_XE]:
            commands = [
                f"vlan {vlan_id}",
                f"name {vlan_name}",
                "exit"
            ]
        elif device_type == NetworkVendor.JUNIPER_JUNOS:
            commands = [
                f"set vlans {vlan_name} vlan-id {vlan_id}"
            ]
        elif device_type == NetworkVendor.ARISTA_EOS:
            commands = [
                f"vlan {vlan_id}",
                f"name {vlan_name}"
            ]
        else:
            return ExecutionResult(
                success=False,
                error=f"VLAN configuration not supported for {device_type.value}"
            )
        
        try:
            connection = self.active_connections[device_key]['connection']
            
            output = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: connection.send_config_set(commands)
            )
            
            # Save configuration
            await self.save_configuration(host, port)
            
            return ExecutionResult(
                success=True,
                stdout=output,
                exit_code=0
            )
            
        except Exception as e:
            self.logger.error(f"VLAN configuration failed: {e}")
            return ExecutionResult(
                success=False,
                error=str(e)
            )
    
    async def configure_interface(
        self,
        host: str,
        interface: str,
        config: Dict[str, Any],
        port: int = 22
    ) -> ExecutionResult:
        """Configure network interface"""
        
        device_key = f"{host}:{port}"
        
        if device_key not in self.active_connections:
            return ExecutionResult(
                success=False,
                error=f"No active connection to {host}"
            )
        
        device_type = self.active_connections[device_key]['device_type']
        
        # Build configuration commands
        commands = [f"interface {interface}"]
        
        if device_type in [NetworkVendor.CISCO_IOS, NetworkVendor.CISCO_XE]:
            if 'description' in config:
                commands.append(f"description {config['description']}")
            if 'ip_address' in config:
                commands.append(f"ip address {config['ip_address']} {config.get('subnet_mask', '255.255.255.0')}")
            if 'vlan' in config:
                commands.append(f"switchport access vlan {config['vlan']}")
            if 'mode' in config:
                commands.append(f"switchport mode {config['mode']}")
            if config.get('shutdown', False):
                commands.append("shutdown")
            else:
                commands.append("no shutdown")
        
        commands.append("exit")
        
        try:
            connection = self.active_connections[device_key]['connection']
            
            output = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: connection.send_config_set(commands)
            )
            
            await self.save_configuration(host, port)
            
            return ExecutionResult(
                success=True,
                stdout=output,
                exit_code=0
            )
            
        except Exception as e:
            self.logger.error(f"Interface configuration failed: {e}")
            return ExecutionResult(
                success=False,
                error=str(e)
            )
    
    async def configure_routing(
        self,
        host: str,
        network: str,
        mask: str,
        next_hop: str,
        port: int = 22
    ) -> ExecutionResult:
        """Configure static route"""
        
        device_key = f"{host}:{port}"
        
        if device_key not in self.active_connections:
            return ExecutionResult(
                success=False,
                error=f"No active connection to {host}"
            )
        
        device_type = self.active_connections[device_key]['device_type']
        
        if device_type in [NetworkVendor.CISCO_IOS, NetworkVendor.CISCO_XE]:
            command = f"ip route {network} {mask} {next_hop}"
        elif device_type == NetworkVendor.JUNIPER_JUNOS:
            command = f"set routing-options static route {network}/{mask} next-hop {next_hop}"
        elif device_type == NetworkVendor.ARISTA_EOS:
            command = f"ip route {network}/{mask} {next_hop}"
        else:
            return ExecutionResult(
                success=False,
                error=f"Routing configuration not supported for {device_type.value}"
            )
        
        try:
            connection = self.active_connections[device_key]['connection']
            
            output = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: connection.send_config_set([command])
            )
            
            await self.save_configuration(host, port)
            
            return ExecutionResult(
                success=True,
                stdout=output,
                exit_code=0
            )
            
        except Exception as e:
            self.logger.error(f"Routing configuration failed: {e}")
            return ExecutionResult(
                success=False,
                error=str(e)
            )
    
    async def configure_acl(
        self,
        host: str,
        acl_name: str,
        rules: List[Dict[str, Any]],
        port: int = 22
    ) -> ExecutionResult:
        """Configure Access Control List"""
        
        device_key = f"{host}:{port}"
        
        if device_key not in self.active_connections:
            return ExecutionResult(
                success=False,
                error=f"No active connection to {host}"
            )
        
        device_type = self.active_connections[device_key]['device_type']
        commands = []
        
        if device_type in [NetworkVendor.CISCO_IOS, NetworkVendor.CISCO_XE]:
            commands.append(f"ip access-list extended {acl_name}")
            
            for rule in rules:
                action = rule.get('action', 'permit')
                protocol = rule.get('protocol', 'ip')
                source = rule.get('source', 'any')
                destination = rule.get('destination', 'any')
                
                commands.append(f"{action} {protocol} {source} {destination}")
            
            commands.append("exit")
        
        try:
            connection = self.active_connections[device_key]['connection']
            
            output = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: connection.send_config_set(commands)
            )
            
            await self.save_configuration(host, port)
            
            return ExecutionResult(
                success=True,
                stdout=output,
                exit_code=0
            )
            
        except Exception as e:
            self.logger.error(f"ACL configuration failed: {e}")
            return ExecutionResult(
                success=False,
                error=str(e)
            )
    
    async def block_ip_address(
        self,
        host: str,
        ip_address: str,
        port: int = 22
    ) -> ExecutionResult:
        """Block an IP address (for brute force attacks)"""
        
        self.logger.info(f"🛡️ Blocking IP {ip_address} on {host}")
        
        # Create ACL rule to block the IP
        rules = [
            {
                'action': 'deny',
                'protocol': 'ip',
                'source': ip_address,
                'destination': 'any'
            }
        ]
        
        return await self.configure_acl(
            host,
            f"BLOCK_{ip_address.replace('.', '_')}",
            rules,
            port
        )
    
    async def get_device_info(
        self,
        host: str,
        port: int = 22
    ) -> Dict[str, Any]:
        """Get device information"""
        
        device_key = f"{host}:{port}"
        
        if device_key not in self.active_connections:
            return {'error': f"No active connection to {host}"}
        
        device_type = self.active_connections[device_key]['device_type']
        
        # Get version info
        if device_type in [NetworkVendor.CISCO_IOS, NetworkVendor.CISCO_XE]:
            version_cmd = "show version"
            interfaces_cmd = "show ip interface brief"
        elif device_type == NetworkVendor.JUNIPER_JUNOS:
            version_cmd = "show version"
            interfaces_cmd = "show interfaces terse"
        elif device_type == NetworkVendor.ARISTA_EOS:
            version_cmd = "show version"
            interfaces_cmd = "show ip interface brief"
        else:
            version_cmd = "show version"
            interfaces_cmd = "show interfaces"
        
        try:
            version_result = await self.execute_command(host, version_cmd, port)
            interfaces_result = await self.execute_command(host, interfaces_cmd, port)
            
            return {
                'host': host,
                'device_type': device_type.value,
                'version': version_result.stdout,
                'interfaces': interfaces_result.stdout,
                'connected': True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get device info: {e}")
            return {'error': str(e)}
    
    async def discover_topology(
        self,
        seed_devices: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Discover network topology using CDP/LLDP"""
        
        topology = {
            'devices': {},
            'links': []
        }
        
        for device in seed_devices:
            try:
                # Connect to device
                connected = await self.connect_device(
                    host=device['host'],
                    username=device['username'],
                    password=device['password'],
                    device_type=NetworkVendor[device['device_type']],
                    enable_password=device.get('enable_password')
                )
                
                if not connected:
                    continue
                
                # Get CDP/LLDP neighbors
                result = await self.execute_command(
                    device['host'],
                    "show cdp neighbors detail"
                )
                
                if result.success:
                    # Parse neighbors and add to topology
                    neighbors = self.parse_cdp_neighbors(result.stdout)
                    topology['devices'][device['host']] = neighbors
                
            except Exception as e:
                self.logger.error(f"Topology discovery failed for {device['host']}: {e}")
        
        return topology
    
    def parse_cdp_neighbors(self, output: str) -> List[Dict[str, str]]:
        """Parse CDP neighbors output"""
        neighbors = []
        
        # Simple parsing - in production, use more robust parsing
        lines = output.split('\n')
        current_neighbor = {}
        
        for line in lines:
            if 'Device ID:' in line:
                if current_neighbor:
                    neighbors.append(current_neighbor)
                current_neighbor = {'device_id': line.split(':')[1].strip()}
            elif 'IP address:' in line:
                current_neighbor['ip_address'] = line.split(':')[1].strip()
            elif 'Platform:' in line:
                current_neighbor['platform'] = line.split(':')[1].strip()
        
        if current_neighbor:
            neighbors.append(current_neighbor)
        
        return neighbors
    
    async def save_configuration(self, host: str, port: int = 22):
        """Save device configuration"""
        
        device_key = f"{host}:{port}"
        
        if device_key not in self.active_connections:
            return
        
        device_type = self.active_connections[device_key]['device_type']
        connection = self.active_connections[device_key]['connection']
        
        try:
            if device_type in [NetworkVendor.CISCO_IOS, NetworkVendor.CISCO_XE]:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: connection.save_config()
                )
                self.logger.info(f"✅ Configuration saved on {host}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration on {host}: {e}")
    
    async def disconnect_device(self, host: str, port: int = 22):
        """Disconnect from device"""
        
        device_key = f"{host}:{port}"
        
        if device_key in self.active_connections:
            try:
                connection = self.active_connections[device_key]['connection']
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    connection.disconnect
                )
                del self.active_connections[device_key]
                self.logger.info(f"Disconnected from {host}")
            except Exception as e:
                self.logger.error(f"Error disconnecting from {host}: {e}")
    
    async def disconnect_all(self):
        """Disconnect from all devices"""
        
        for device_key in list(self.active_connections.keys()):
            host = self.active_connections[device_key]['host']
            await self.disconnect_device(host)