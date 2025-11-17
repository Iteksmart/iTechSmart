"""
iTechSmart Supreme Plus - Configuration Management
Handles all configuration settings for the platform

Copyright (c) 2025 iTechSmart Suite
Launch Date: August 8, 2025
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "iTechSmart Supreme Plus"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://supremeplus:supremeplus@localhost:5434/supremeplus",
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/4")

    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Integration Settings
    PROMETHEUS_URL: Optional[str] = os.getenv("PROMETHEUS_URL")
    WAZUH_URL: Optional[str] = os.getenv("WAZUH_URL")
    WAZUH_API_KEY: Optional[str] = os.getenv("WAZUH_API_KEY")

    # SSH Settings
    SSH_TIMEOUT: int = int(os.getenv("SSH_TIMEOUT", "30"))
    SSH_MAX_RETRIES: int = int(os.getenv("SSH_MAX_RETRIES", "3"))

    # Remediation Settings
    AUTO_REMEDIATION_ENABLED: bool = (
        os.getenv("AUTO_REMEDIATION_ENABLED", "true").lower() == "true"
    )
    REMEDIATION_TIMEOUT: int = int(os.getenv("REMEDIATION_TIMEOUT", "300"))
    MAX_CONCURRENT_REMEDIATIONS: int = int(
        os.getenv("MAX_CONCURRENT_REMEDIATIONS", "10")
    )

    # AI Settings
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "2000"))

    # Monitoring Settings
    METRICS_RETENTION_DAYS: int = int(os.getenv("METRICS_RETENTION_DAYS", "30"))
    ALERT_CHECK_INTERVAL: int = int(os.getenv("ALERT_CHECK_INTERVAL", "60"))

    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "supreme-plus-secret-key-change-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/supreme_plus.log")

    # iTechSmart Hub Integration
    HUB_URL: str = os.getenv("HUB_URL", "http://localhost:8000")
    HUB_API_KEY: Optional[str] = os.getenv("HUB_API_KEY")

    # iTechSmart Ninja Integration
    NINJA_URL: str = os.getenv("NINJA_URL", "http://localhost:8001")
    NINJA_API_KEY: Optional[str] = os.getenv("NINJA_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Remediation action templates
REMEDIATION_TEMPLATES = {
    "restart_service": {
        "name": "Restart Service",
        "description": "Restart a system service",
        "commands": {
            "linux": "sudo systemctl restart {service_name}",
            "windows": "Restart-Service -Name {service_name} -Force",
        },
    },
    "clear_disk_space": {
        "name": "Clear Disk Space",
        "description": "Clear temporary files and logs",
        "commands": {
            "linux": "sudo find /tmp -type f -atime +7 -delete && sudo journalctl --vacuum-time=7d",
            "windows": "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue",
        },
    },
    "restart_container": {
        "name": "Restart Container",
        "description": "Restart a Docker container",
        "commands": {
            "linux": "docker restart {container_name}",
            "windows": "docker restart {container_name}",
        },
    },
    "scale_service": {
        "name": "Scale Service",
        "description": "Scale a service up or down",
        "commands": {
            "kubernetes": "kubectl scale deployment {deployment_name} --replicas={replicas}",
            "docker_swarm": "docker service scale {service_name}={replicas}",
        },
    },
    "clear_cache": {
        "name": "Clear Cache",
        "description": "Clear application cache",
        "commands": {
            "redis": "redis-cli FLUSHDB",
            "memcached": "echo 'flush_all' | nc localhost 11211",
        },
    },
    "restart_database": {
        "name": "Restart Database",
        "description": "Restart database service",
        "commands": {
            "postgresql": "sudo systemctl restart postgresql",
            "mysql": "sudo systemctl restart mysql",
            "mongodb": "sudo systemctl restart mongod",
        },
    },
    "kill_process": {
        "name": "Kill Process",
        "description": "Terminate a running process",
        "commands": {
            "linux": "sudo kill -9 {pid}",
            "windows": "Stop-Process -Id {pid} -Force",
        },
    },
    "update_firewall": {
        "name": "Update Firewall",
        "description": "Update firewall rules",
        "commands": {
            "linux": "sudo ufw {action} {port}",
            "windows": "netsh advfirewall firewall {action} rule name={rule_name}",
        },
    },
    "restart_workstation": {
        "name": "Restart Workstation",
        "description": "Restart a workstation",
        "commands": {
            "linux": "sudo shutdown -r now",
            "windows": "Restart-Computer -Force",
        },
    },
    "fix_network_adapter": {
        "name": "Fix Network Adapter",
        "description": "Reset network adapter",
        "commands": {
            "linux": "sudo systemctl restart NetworkManager",
            "windows": "Get-NetAdapter | Restart-NetAdapter",
        },
    },
    "clear_dns_cache": {
        "name": "Clear DNS Cache",
        "description": "Flush DNS resolver cache",
        "commands": {
            "linux": "sudo systemd-resolve --flush-caches",
            "windows": "ipconfig /flushdns",
        },
    },
    "fix_printer": {
        "name": "Fix Printer",
        "description": "Restart print spooler service",
        "commands": {
            "linux": "sudo systemctl restart cups",
            "windows": "Restart-Service -Name Spooler -Force",
        },
    },
    "reset_user_profile": {
        "name": "Reset User Profile",
        "description": "Reset user profile cache",
        "commands": {
            "linux": "rm -rf ~/.cache/*",
            "windows": "Remove-Item -Path $env:LOCALAPPDATA\\Temp\\* -Recurse -Force",
        },
    },
    "update_software": {
        "name": "Update Software",
        "description": "Update system packages",
        "commands": {
            "linux": "sudo apt update && sudo apt upgrade -y",
            "windows": "Get-WindowsUpdate -Install -AcceptAll -AutoReboot",
        },
    },
    "fix_audio": {
        "name": "Fix Audio",
        "description": "Restart audio service",
        "commands": {
            "linux": "pulseaudio -k && pulseaudio --start",
            "windows": "Restart-Service -Name Audiosrv -Force",
        },
    },
    "check_server_health": {
        "name": "Check Server Health",
        "description": "Run comprehensive server health check",
        "commands": {
            "linux": "df -h && free -m && uptime && systemctl status",
            "windows": "Get-ComputerInfo | Select-Object CsName,OsVersion,OsUptime",
        },
    },
    "optimize_server": {
        "name": "Optimize Server",
        "description": "Optimize server performance",
        "commands": {
            "linux": "sync && echo 3 > /proc/sys/vm/drop_caches",
            "windows": "Clear-RecycleBin -Force; Optimize-Volume -DriveLetter C -Defrag",
        },
    },
    "backup_server": {
        "name": "Backup Server",
        "description": "Create server backup",
        "commands": {
            "linux": "tar -czf /backup/server-$(date +%Y%m%d).tar.gz /etc /var/www /home",
            "windows": "wbadmin start backup -backupTarget:{backup_target} -include:{volumes}",
        },
    },
    "reload_network_device": {
        "name": "Reload Network Device",
        "description": "Reload network device configuration",
        "commands": {
            "cisco": "reload in 1",
            "juniper": "request system reboot",
            "palo_alto": "request restart system",
        },
    },
    "save_network_config": {
        "name": "Save Network Config",
        "description": "Save running configuration",
        "commands": {
            "cisco": "write memory",
            "juniper": "commit",
            "palo_alto": "commit",
        },
    },
    "clear_arp_cache": {
        "name": "Clear ARP Cache",
        "description": "Clear ARP table",
        "commands": {
            "cisco": "clear arp-cache",
            "juniper": "clear arp",
            "palo_alto": "clear arp all",
            "linux": "sudo ip -s -s neigh flush all",
        },
    },
    "reset_interface": {
        "name": "Reset Interface",
        "description": "Reset network interface",
        "commands": {
            "cisco": "interface {interface}; shutdown; no shutdown",
            "juniper": "set interfaces {interface} disable; commit",
            "palo_alto": "set network interface ethernet {interface} link-state down",
        },
    },
    "check_disk_health": {
        "name": "Check Disk Health",
        "description": "Check disk health status",
        "commands": {
            "linux": "sudo smartctl -a /dev/sda",
            "windows": "Get-PhysicalDisk | Get-StorageReliabilityCounter",
        },
    },
}

# Incident severity levels
SEVERITY_LEVELS = {
    "critical": {
        "priority": 1,
        "auto_remediate": True,
        "notification_channels": ["email", "sms", "slack", "pagerduty"],
    },
    "high": {
        "priority": 2,
        "auto_remediate": True,
        "notification_channels": ["email", "slack"],
    },
    "medium": {
        "priority": 3,
        "auto_remediate": False,
        "notification_channels": ["email"],
    },
    "low": {"priority": 4, "auto_remediate": False, "notification_channels": []},
}

# Integration types
INTEGRATION_TYPES = [
    "prometheus",
    "wazuh",
    "grafana",
    "elasticsearch",
    "splunk",
    "datadog",
    "new_relic",
    "pagerduty",
    "slack",
    "webhook",
]

# Network device types and connection methods
NETWORK_DEVICE_TYPES = {
    "cisco_ios": {
        "name": "Cisco IOS",
        "connection": "ssh",
        "port": 22,
        "enable_mode": True,
        "prompt": "#",
    },
    "cisco_nxos": {
        "name": "Cisco NX-OS",
        "connection": "ssh",
        "port": 22,
        "enable_mode": False,
        "prompt": "#",
    },
    "juniper_junos": {
        "name": "Juniper JunOS",
        "connection": "ssh",
        "port": 22,
        "enable_mode": False,
        "prompt": ">",
    },
    "palo_alto": {
        "name": "Palo Alto",
        "connection": "ssh",
        "port": 22,
        "enable_mode": False,
        "prompt": ">",
    },
    "f5_bigip": {
        "name": "F5 BIG-IP",
        "connection": "ssh",
        "port": 22,
        "enable_mode": False,
        "prompt": "#",
    },
    "arista_eos": {
        "name": "Arista EOS",
        "connection": "ssh",
        "port": 22,
        "enable_mode": True,
        "prompt": "#",
    },
    "hp_procurve": {
        "name": "HP ProCurve",
        "connection": "ssh",
        "port": 22,
        "enable_mode": False,
        "prompt": "#",
    },
}

# Workstation-specific remediation actions
WORKSTATION_ACTIONS = {
    "restart_explorer": {
        "name": "Restart Windows Explorer",
        "description": "Restart Windows Explorer process",
        "command": "Stop-Process -Name explorer -Force; Start-Process explorer",
    },
    "fix_display": {
        "name": "Fix Display Issues",
        "description": "Reset display drivers",
        "command": "Get-PnpDevice -Class Display | Disable-PnpDevice -Confirm:$false; Get-PnpDevice -Class Display | Enable-PnpDevice -Confirm:$false",
    },
    "clear_temp_files": {
        "name": "Clear Temporary Files",
        "description": "Remove all temporary files",
        "command": "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue",
    },
    "fix_windows_update": {
        "name": "Fix Windows Update",
        "description": "Reset Windows Update components",
        "command": "Stop-Service wuauserv,bits; Remove-Item C:\\Windows\\SoftwareDistribution -Recurse -Force; Start-Service wuauserv,bits",
    },
    "repair_network": {
        "name": "Repair Network Connection",
        "description": "Reset network stack",
        "command": "netsh winsock reset; netsh int ip reset; ipconfig /release; ipconfig /renew",
    },
}

# Server-specific remediation actions
SERVER_ACTIONS = {
    "check_raid": {
        "name": "Check RAID Status",
        "description": "Check hardware RAID status",
        "linux": "sudo cat /proc/mdstat",
        "windows": "Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus",
    },
    "monitor_resources": {
        "name": "Monitor Resources",
        "description": "Check CPU, memory, disk usage",
        "linux": "top -bn1 | head -20; df -h; free -m",
        "windows": "Get-Counter '\\Processor(_Total)\\% Processor Time','\\Memory\\Available MBytes','\\PhysicalDisk(_Total)\\% Disk Time'",
    },
    "check_services": {
        "name": "Check Critical Services",
        "description": "Verify critical services are running",
        "linux": "systemctl list-units --type=service --state=running",
        "windows": "Get-Service | Where-Object {$_.Status -eq 'Running'}",
    },
    "analyze_logs": {
        "name": "Analyze System Logs",
        "description": "Check for errors in system logs",
        "linux": "journalctl -p err -n 50",
        "windows": "Get-EventLog -LogName System -EntryType Error -Newest 50",
    },
}

# Network device command libraries
NETWORK_COMMANDS = {
    "cisco": {
        "show_version": "show version",
        "show_interfaces": "show ip interface brief",
        "show_routes": "show ip route",
        "show_config": "show running-config",
        "save_config": "write memory",
        "reload": "reload",
        "show_arp": "show arp",
        "show_mac": "show mac address-table",
        "show_vlan": "show vlan brief",
        "ping": "ping {target}",
        "traceroute": "traceroute {target}",
    },
    "juniper": {
        "show_version": "show version",
        "show_interfaces": "show interfaces terse",
        "show_routes": "show route",
        "show_config": "show configuration",
        "save_config": "commit",
        "reload": "request system reboot",
        "show_arp": "show arp",
        "show_mac": "show ethernet-switching table",
        "show_vlan": "show vlans",
        "ping": "ping {target}",
        "traceroute": "traceroute {target}",
    },
    "palo_alto": {
        "show_version": "show system info",
        "show_interfaces": "show interface all",
        "show_routes": "show routing route",
        "show_config": "show config running",
        "save_config": "commit",
        "reload": "request restart system",
        "show_arp": "show arp all",
        "show_sessions": "show session all",
        "ping": "ping host {target}",
        "traceroute": "traceroute host {target}",
    },
}
