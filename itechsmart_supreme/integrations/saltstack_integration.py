"""
SaltStack Integration - Automation and Infrastructure Management
Execute Salt states and commands for infrastructure automation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import subprocess
import json
import yaml

from ..core.models import RemediationAction, ExecutionResult, Platform


class SaltStackIntegration:
    """Integration with SaltStack for infrastructure management"""

    def __init__(self, master_url: Optional[str] = None):
        self.master_url = master_url or "salt://master"
        self.logger = logging.getLogger(__name__)

    async def execute_command(
        self,
        target: str,
        function: str,
        args: Optional[List[str]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        timeout: int = 60,
    ) -> ExecutionResult:
        """Execute Salt command on minions"""

        self.logger.info(f"Executing Salt command: {function} on {target}")

        cmd = ["salt", target, function]

        if args:
            cmd.extend(args)

        if kwargs:
            for key, value in kwargs.items():
                cmd.append(f"{key}={value}")

        cmd.extend(["--out=json", f"--timeout={timeout}"])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout + 10
            )

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode("utf-8"),
                stderr=stderr.decode("utf-8"),
                exit_code=process.returncode,
            )

        except asyncio.TimeoutError:
            self.logger.error(f"Salt command timed out after {timeout}s")
            return ExecutionResult(
                success=False, error="Command timed out", stderr="Command timed out"
            )

        except Exception as e:
            self.logger.error(f"Salt command execution failed: {e}")
            return ExecutionResult(success=False, error=str(e), stderr=str(e))

    async def apply_state(
        self,
        target: str,
        state: str,
        pillar: Optional[Dict[str, Any]] = None,
        test: bool = False,
    ) -> ExecutionResult:
        """Apply Salt state to minions"""

        self.logger.info(f"Applying Salt state: {state} to {target}")

        cmd = ["salt", target, "state.apply", state, "--out=json"]

        if pillar:
            cmd.append(f"pillar={json.dumps(pillar)}")

        if test:
            cmd.append("test=True")

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
            self.logger.error(f"Salt state application failed: {e}")
            return ExecutionResult(success=False, error=str(e), stderr=str(e))

    async def execute_remediation(
        self, action: RemediationAction, target: str
    ) -> ExecutionResult:
        """Execute remediation action using Salt"""

        if action.platform == Platform.LINUX:
            return await self.execute_command(
                target=target, function="cmd.run", args=[action.command]
            )

        elif action.platform == Platform.WINDOWS:
            return await self.execute_command(
                target=target,
                function="cmd.run",
                args=[action.command],
                kwargs={"shell": "powershell"},
            )

        else:
            return ExecutionResult(
                success=False, error=f"Unsupported platform: {action.platform}"
            )

    async def get_grains(self, target: str = "*") -> Dict[str, Any]:
        """Get grains (system information) from minions"""

        result = await self.execute_command(target=target, function="grains.items")

        if result.success:
            try:
                return json.loads(result.stdout)
            except Exception as e:
                self.logger.error(f"Failed to parse grains: {e}")
                return {}

        return {}

    async def check_connectivity(self, target: str = "*") -> Dict[str, bool]:
        """Check connectivity to minions"""

        result = await self.execute_command(target=target, function="test.ping")

        if result.success:
            try:
                return json.loads(result.stdout)
            except Exception as e:
                self.logger.error(f"Failed to parse ping results: {e}")
                return {}

        return {}

    async def install_package(
        self, target: str, package: str, version: Optional[str] = None
    ) -> ExecutionResult:
        """Install package on minions"""

        args = [package]
        if version:
            args.append(f"version={version}")

        return await self.execute_command(
            target=target, function="pkg.install", args=args
        )

    async def restart_service(self, target: str, service: str) -> ExecutionResult:
        """Restart service on minions"""

        return await self.execute_command(
            target=target, function="service.restart", args=[service]
        )

    async def copy_file(
        self, target: str, source: str, destination: str, makedirs: bool = True
    ) -> ExecutionResult:
        """Copy file to minions"""

        return await self.execute_command(
            target=target,
            function="cp.get_file",
            args=[source, destination],
            kwargs={"makedirs": makedirs},
        )

    async def execute_script(
        self, target: str, script: str, args: Optional[List[str]] = None
    ) -> ExecutionResult:
        """Execute script on minions"""

        cmd_args = [script]
        if args:
            cmd_args.extend(args)

        return await self.execute_command(
            target=target, function="cmd.script", args=cmd_args
        )

    async def get_pillar(
        self, target: str, key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get pillar data from minions"""

        function = "pillar.items" if not key else "pillar.get"
        args = [key] if key else None

        result = await self.execute_command(target=target, function=function, args=args)

        if result.success:
            try:
                return json.loads(result.stdout)
            except Exception as e:
                self.logger.error(f"Failed to parse pillar data: {e}")
                return {}

        return {}

    async def highstate(self, target: str, test: bool = False) -> ExecutionResult:
        """Apply highstate to minions"""

        cmd = ["salt", target, "state.highstate", "--out=json"]

        if test:
            cmd.append("test=True")

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
            self.logger.error(f"Highstate execution failed: {e}")
            return ExecutionResult(success=False, error=str(e), stderr=str(e))

    async def get_job_status(self, jid: str) -> Dict[str, Any]:
        """Get status of a Salt job"""

        result = await self.execute_command(
            target="*", function="saltutil.find_job", args=[jid]
        )

        if result.success:
            try:
                return json.loads(result.stdout)
            except Exception as e:
                self.logger.error(f"Failed to parse job status: {e}")
                return {}

        return {}

    async def sync_all(self, target: str = "*") -> ExecutionResult:
        """Sync all Salt modules to minions"""

        return await self.execute_command(target=target, function="saltutil.sync_all")

    async def refresh_pillar(self, target: str = "*") -> ExecutionResult:
        """Refresh pillar data on minions"""

        return await self.execute_command(
            target=target, function="saltutil.refresh_pillar"
        )
