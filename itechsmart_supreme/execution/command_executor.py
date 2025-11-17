"""
Secure command execution engine supporting SSH, WinRM, Telnet
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import re

import paramiko
import winrm
from telnetlib3 import open_connection

from ..core.models import (
    RemediationAction,
    ExecutionResult,
    HostCredentials,
    ActionStatus,
    Platform,
    SeverityLevel,
)


class SecureCommandExecutor:
    """Execute commands securely across multiple platforms"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.execution_log = []
        self.sandbox_mode = False
        self.approved_commands = set()
        self.global_kill_switch = False

    def enable_kill_switch(self):
        """Enable global kill switch - stops all executions"""
        self.global_kill_switch = True
        self.logger.critical("GLOBAL KILL SWITCH ENABLED - All executions stopped")

    def disable_kill_switch(self):
        """Disable global kill switch"""
        self.global_kill_switch = False
        self.logger.info("Global kill switch disabled")

    async def execute_remediation(
        self, action: RemediationAction, credentials: HostCredentials
    ) -> ExecutionResult:
        """Execute a remediation action"""

        # Check global kill switch
        if self.global_kill_switch:
            return ExecutionResult(
                action_id=action.id,
                success=False,
                error="Global kill switch is enabled - execution blocked",
            )

        # Validate command safety
        if not await self.validate_command_safety(action):
            return ExecutionResult(
                action_id=action.id,
                success=False,
                error="Command failed safety validation",
            )

        # Check approval status
        if action.requires_approval and action.status != ActionStatus.APPROVED:
            return ExecutionResult(
                action_id=action.id,
                success=False,
                error="Action requires approval before execution",
            )

        # Update action status
        action.status = ActionStatus.EXECUTING
        action.executed_at = datetime.now()

        execution_id = str(uuid.uuid4())
        start_time = datetime.now()

        try:
            # Execute based on platform
            if credentials.platform == Platform.LINUX:
                result = await self.execute_ssh_command(
                    action.command, credentials, execution_id
                )
            elif credentials.platform == Platform.WINDOWS:
                result = await self.execute_winrm_command(
                    action.command, credentials, execution_id
                )
            elif credentials.platform == Platform.NETWORK:
                result = await self.execute_telnet_command(
                    action.command, credentials, execution_id
                )
            else:
                raise ValueError(f"Unsupported platform: {credentials.platform}")

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time

            # Update action status
            if result.success:
                action.status = ActionStatus.EXECUTED
            else:
                action.status = ActionStatus.FAILED

            action.execution_result = {
                "execution_id": result.execution_id,
                "success": result.success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
            }

            # Log execution
            self.log_execution(action, result, execution_id)

            return result

        except Exception as e:
            self.logger.error(f"Execution failed: {e}")

            error_result = ExecutionResult(
                execution_id=execution_id,
                action_id=action.id,
                success=False,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds(),
            )

            action.status = ActionStatus.FAILED
            action.execution_result = {
                "execution_id": execution_id,
                "success": False,
                "error": str(e),
            }

            self.log_execution(action, error_result, execution_id)

            return error_result

    async def execute_ssh_command(
        self, command: str, credentials: HostCredentials, execution_id: str
    ) -> ExecutionResult:
        """Execute command via SSH"""

        self.logger.info(f"Executing SSH command on {credentials.host}: {command}")

        try:
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect
            connect_kwargs = {
                "hostname": credentials.host,
                "username": credentials.username,
                "port": credentials.port,
                "timeout": 30,
            }

            if credentials.password:
                connect_kwargs["password"] = credentials.password
            elif credentials.private_key:
                connect_kwargs["key_filename"] = credentials.private_key

            ssh.connect(**connect_kwargs)

            # Add sudo if required
            if credentials.use_sudo and not command.startswith("sudo"):
                command = f"sudo {command}"

            # Execute command
            stdin, stdout, stderr = ssh.exec_command(command, timeout=300)

            # Get results
            stdout_data = stdout.read().decode("utf-8", errors="ignore")
            stderr_data = stderr.read().decode("utf-8", errors="ignore")
            exit_code = stdout.channel.recv_exit_status()

            ssh.close()

            return ExecutionResult(
                execution_id=execution_id,
                success=exit_code == 0,
                stdout=stdout_data,
                stderr=stderr_data,
                exit_code=exit_code,
            )

        except Exception as e:
            self.logger.error(f"SSH execution failed: {e}")
            return ExecutionResult(
                execution_id=execution_id, success=False, error=str(e), stderr=str(e)
            )

    async def execute_winrm_command(
        self, command: str, credentials: HostCredentials, execution_id: str
    ) -> ExecutionResult:
        """Execute command via WinRM (PowerShell)"""

        self.logger.info(f"Executing WinRM command on {credentials.host}: {command}")

        try:
            # Create WinRM session
            protocol = "https" if credentials.port == 5986 else "http"
            endpoint = f"{protocol}://{credentials.host}:{credentials.port}/wsman"

            # Handle domain credentials
            if credentials.domain:
                username = f"{credentials.domain}\\{credentials.username}"
            else:
                username = credentials.username

            session = winrm.Session(
                endpoint,
                auth=(username, credentials.password),
                server_cert_validation="ignore",
            )

            # Execute PowerShell command
            result = session.run_ps(command)

            return ExecutionResult(
                execution_id=execution_id,
                success=result.status_code == 0,
                stdout=result.std_out.decode("utf-8", errors="ignore"),
                stderr=result.std_err.decode("utf-8", errors="ignore"),
                exit_code=result.status_code,
            )

        except Exception as e:
            self.logger.error(f"WinRM execution failed: {e}")
            return ExecutionResult(
                execution_id=execution_id, success=False, error=str(e), stderr=str(e)
            )

    async def execute_telnet_command(
        self, command: str, credentials: HostCredentials, execution_id: str
    ) -> ExecutionResult:
        """Execute command via Telnet (for network devices)"""

        self.logger.info(f"Executing Telnet command on {credentials.host}: {command}")

        try:
            # Connect via Telnet
            reader, writer = await open_connection(
                credentials.host,
                credentials.port if credentials.port != 22 else 23,
                connect_minwait=1.0,
            )

            # Wait for login prompt
            output = await asyncio.wait_for(reader.read(1024), timeout=10)

            # Send username
            writer.write(credentials.username + "\n")
            output += await asyncio.wait_for(reader.read(1024), timeout=10)

            # Send password
            writer.write(credentials.password + "\n")
            output += await asyncio.wait_for(reader.read(1024), timeout=10)

            # Send command
            writer.write(command + "\n")

            # Read output
            command_output = await asyncio.wait_for(reader.read(4096), timeout=30)

            # Close connection
            writer.close()

            return ExecutionResult(
                execution_id=execution_id,
                success=True,
                stdout=command_output,
                exit_code=0,
            )

        except Exception as e:
            self.logger.error(f"Telnet execution failed: {e}")
            return ExecutionResult(
                execution_id=execution_id, success=False, error=str(e), stderr=str(e)
            )

    async def validate_command_safety(self, action: RemediationAction) -> bool:
        """Validate that a command is safe to execute"""

        command = action.command.lower()

        # Dangerous command patterns
        dangerous_patterns = [
            r"rm\s+-rf\s+/",
            r"del\s+/[qsf]\s+\*",
            r"format\s+c:",
            r"dd\s+if=.*of=/dev/[sh]d",
            r"mkfs\.",
            r"fdisk",
            r"parted.*rm",
            r":(){ :|:& };:",  # Fork bomb
            r"chmod\s+777\s+/",
            r"chown\s+.*\s+/",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                self.logger.warning(f"Dangerous command pattern detected: {pattern}")
                return False

        # Check risk level
        if action.risk_level == SeverityLevel.CRITICAL:
            self.logger.warning("Critical risk action requires manual approval")
            return False

        # Check if command is in approved list
        if action.command in self.approved_commands:
            return True

        # Additional platform-specific checks
        if action.platform == Platform.WINDOWS:
            windows_dangerous = [
                "shutdown",
                "restart-computer",
                "remove-item -recurse c:\\",
            ]
            for dangerous in windows_dangerous:
                if dangerous in command:
                    self.logger.warning(
                        f"Dangerous Windows command detected: {dangerous}"
                    )
                    return False

        return True

    def log_execution(
        self, action: RemediationAction, result: ExecutionResult, execution_id: str
    ):
        """Log command execution for audit trail"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "execution_id": execution_id,
            "action_id": action.id,
            "alert_id": action.alert_id,
            "command": action.command,
            "platform": action.platform.value,
            "success": result.success,
            "stdout": (
                result.stdout[:500] if result.stdout else ""
            ),  # Truncate for storage
            "stderr": result.stderr[:500] if result.stderr else "",
            "exit_code": result.exit_code,
            "execution_time": result.execution_time,
            "risk_level": action.risk_level.value,
            "requires_approval": action.requires_approval,
            "approved_by": action.approved_by,
        }

        self.execution_log.append(log_entry)

        # Log to file/database
        self.logger.info(
            f"Command executed: {execution_id} - Success: {result.success}"
        )

    def get_execution_history(self, limit: int = 100) -> list:
        """Get execution history"""
        return self.execution_log[-limit:]

    def approve_command(self, command: str):
        """Add command to approved list"""
        self.approved_commands.add(command)
        self.logger.info(f"Command approved: {command}")
