"""
Ansible Integration - Automation for Configuration Management
Execute Ansible playbooks for infrastructure automation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import subprocess
import json
import yaml
import tempfile
import os

from ..core.models import RemediationAction, ExecutionResult, Platform


class AnsibleIntegration:
    """Integration with Ansible for configuration management and automation"""

    def __init__(self, inventory_path: Optional[str] = None):
        self.inventory_path = inventory_path or "/etc/ansible/hosts"
        self.logger = logging.getLogger(__name__)
        self.playbook_cache = {}

    async def execute_playbook(
        self,
        playbook_path: str,
        hosts: str = "all",
        extra_vars: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        check_mode: bool = False,
    ) -> ExecutionResult:
        """Execute an Ansible playbook"""

        self.logger.info(f"Executing Ansible playbook: {playbook_path}")

        # Build ansible-playbook command
        cmd = [
            "ansible-playbook",
            playbook_path,
            "-i",
            self.inventory_path,
            "--limit",
            hosts,
        ]

        # Add extra variables
        if extra_vars:
            cmd.extend(["--extra-vars", json.dumps(extra_vars)])

        # Add tags
        if tags:
            cmd.extend(["--tags", ",".join(tags)])

        # Add check mode
        if check_mode:
            cmd.append("--check")

        # Add JSON output
        cmd.extend(["-v", "--json"])

        try:
            # Execute playbook
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode("utf-8"),
                stderr=stderr.decode("utf-8"),
                exit_code=process.returncode,
            )

        except Exception as e:
            self.logger.error(f"Ansible playbook execution failed: {e}")
            return ExecutionResult(success=False, error=str(e), stderr=str(e))

    async def execute_ad_hoc(
        self, module: str, args: str, hosts: str = "all", become: bool = False
    ) -> ExecutionResult:
        """Execute an Ansible ad-hoc command"""

        self.logger.info(f"Executing Ansible ad-hoc: {module} {args}")

        cmd = ["ansible", hosts, "-i", self.inventory_path, "-m", module, "-a", args]

        if become:
            cmd.append("--become")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode("utf-8"),
                stderr=stderr.decode("utf-8"),
                exit_code=process.returncode,
            )

        except Exception as e:
            self.logger.error(f"Ansible ad-hoc execution failed: {e}")
            return ExecutionResult(success=False, error=str(e), stderr=str(e))

    async def create_remediation_playbook(
        self, action: RemediationAction, host: str
    ) -> str:
        """Create an Ansible playbook for remediation action"""

        playbook = {
            "name": f"iTechSmart Remediation: {action.description}",
            "hosts": host,
            "gather_facts": True,
            "tasks": [],
        }

        # Determine task based on platform
        if action.platform == Platform.LINUX:
            playbook["tasks"].append(
                {
                    "name": action.description,
                    "shell": action.command,
                    "register": "result",
                }
            )

        elif action.platform == Platform.WINDOWS:
            playbook["tasks"].append(
                {
                    "name": action.description,
                    "win_shell": action.command,
                    "register": "result",
                }
            )

        # Add result display
        playbook["tasks"].append({"name": "Display result", "debug": {"var": "result"}})

        # Write playbook to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump([playbook], f, default_flow_style=False)
            return f.name

    async def execute_remediation(
        self, action: RemediationAction, host: str
    ) -> ExecutionResult:
        """Execute remediation action using Ansible"""

        # Create playbook
        playbook_path = await self.create_remediation_playbook(action, host)

        try:
            # Execute playbook
            result = await self.execute_playbook(playbook_path, hosts=host)
            return result

        finally:
            # Clean up temporary playbook
            if os.path.exists(playbook_path):
                os.unlink(playbook_path)

    async def get_facts(self, hosts: str = "all") -> Dict[str, Any]:
        """Gather facts from hosts"""

        result = await self.execute_ad_hoc(module="setup", args="", hosts=hosts)

        if result.success:
            try:
                # Parse facts from output
                facts = {}
                for line in result.stdout.split("\n"):
                    if '"ansible_facts"' in line:
                        facts = json.loads(line)
                        break
                return facts
            except Exception as e:
                self.logger.error(f"Failed to parse facts: {e}")
                return {}

        return {}

    async def check_connectivity(self, hosts: str = "all") -> bool:
        """Check connectivity to hosts"""

        result = await self.execute_ad_hoc(module="ping", args="", hosts=hosts)

        return result.success

    async def install_package(
        self, package: str, hosts: str = "all", state: str = "present"
    ) -> ExecutionResult:
        """Install package on hosts"""

        return await self.execute_ad_hoc(
            module="package",
            args=f"name={package} state={state}",
            hosts=hosts,
            become=True,
        )

    async def restart_service(
        self, service: str, hosts: str = "all"
    ) -> ExecutionResult:
        """Restart service on hosts"""

        return await self.execute_ad_hoc(
            module="service",
            args=f"name={service} state=restarted",
            hosts=hosts,
            become=True,
        )

    async def copy_file(
        self, src: str, dest: str, hosts: str = "all", mode: Optional[str] = None
    ) -> ExecutionResult:
        """Copy file to hosts"""

        args = f"src={src} dest={dest}"
        if mode:
            args += f" mode={mode}"

        return await self.execute_ad_hoc(module="copy", args=args, hosts=hosts)

    async def execute_script(
        self, script_path: str, hosts: str = "all"
    ) -> ExecutionResult:
        """Execute script on hosts"""

        return await self.execute_ad_hoc(module="script", args=script_path, hosts=hosts)

    def create_inventory(
        self,
        hosts: Dict[str, Dict[str, Any]],
        groups: Optional[Dict[str, List[str]]] = None,
    ) -> str:
        """Create dynamic inventory"""

        inventory = {}

        # Add hosts
        for hostname, vars in hosts.items():
            inventory[hostname] = vars

        # Add groups
        if groups:
            for group_name, group_hosts in groups.items():
                inventory[group_name] = {"hosts": group_hosts}

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
            for key, value in inventory.items():
                if isinstance(value, dict) and "hosts" in value:
                    f.write(f"[{key}]\n")
                    for host in value["hosts"]:
                        f.write(f"{host}\n")
                else:
                    f.write(f"{key} ")
                    for k, v in value.items():
                        f.write(f"{k}={v} ")
                    f.write("\n")

            return f.name

    async def validate_playbook(self, playbook_path: str) -> bool:
        """Validate Ansible playbook syntax"""

        cmd = ["ansible-playbook", playbook_path, "--syntax-check"]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            await process.communicate()
            return process.returncode == 0

        except Exception as e:
            self.logger.error(f"Playbook validation failed: {e}")
            return False
