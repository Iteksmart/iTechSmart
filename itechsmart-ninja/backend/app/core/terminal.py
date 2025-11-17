"""
Enhanced Terminal Manager for iTechSmart Ninja
Provides full shell access with command history and session management
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import shlex
import subprocess
import threading
import queue

logger = logging.getLogger(__name__)


class TerminalStatus(str, Enum):
    """Terminal session states"""

    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    CLOSED = "closed"
    ERROR = "error"


class CommandStatus(str, Enum):
    """Command execution states"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TerminalConfig:
    """Configuration for terminal session"""

    shell: str = "/bin/bash"
    working_directory: str = "/workspace"
    environment: Dict[str, str] = None
    timeout: int = 300  # 5 minutes default
    max_output_size: int = 10 * 1024 * 1024  # 10MB
    enable_history: bool = True
    max_history_size: int = 1000

    def __post_init__(self):
        if self.environment is None:
            self.environment = {}


@dataclass
class CommandExecution:
    """Information about a command execution"""

    command_id: str
    session_id: str
    command: str
    status: CommandStatus
    started_at: datetime
    completed_at: Optional[datetime]
    exit_code: Optional[int]
    stdout: str
    stderr: str
    execution_time: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "command_id": self.command_id,
            "session_id": self.session_id,
            "command": self.command,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "execution_time": self.execution_time,
        }


@dataclass
class TerminalSession:
    """Terminal session information"""

    session_id: str
    user_id: str
    status: TerminalStatus
    config: TerminalConfig
    created_at: datetime
    last_activity: datetime
    command_history: List[CommandExecution]
    current_directory: str
    environment: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "config": asdict(self.config),
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "command_count": len(self.command_history),
            "current_directory": self.current_directory,
            "environment": self.environment,
        }


class OutputStreamer:
    """Streams command output in real-time"""

    def __init__(self, max_size: int = 10 * 1024 * 1024):
        """Initialize output streamer"""
        self.max_size = max_size
        self.stdout_buffer = []
        self.stderr_buffer = []
        self.stdout_size = 0
        self.stderr_size = 0
        self.subscribers = []

    def add_stdout(self, data: str):
        """Add stdout data"""
        if self.stdout_size + len(data) > self.max_size:
            data = data[: self.max_size - self.stdout_size]

        self.stdout_buffer.append(data)
        self.stdout_size += len(data)
        self._notify_subscribers("stdout", data)

    def add_stderr(self, data: str):
        """Add stderr data"""
        if self.stderr_size + len(data) > self.max_size:
            data = data[: self.max_size - self.stderr_size]

        self.stderr_buffer.append(data)
        self.stderr_size += len(data)
        self._notify_subscribers("stderr", data)

    def get_stdout(self) -> str:
        """Get complete stdout"""
        return "".join(self.stdout_buffer)

    def get_stderr(self) -> str:
        """Get complete stderr"""
        return "".join(self.stderr_buffer)

    def subscribe(self, callback):
        """Subscribe to output updates"""
        self.subscribers.append(callback)

    def _notify_subscribers(self, stream: str, data: str):
        """Notify subscribers of new output"""
        for callback in self.subscribers:
            try:
                callback(stream, data)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")


class TerminalManager:
    """Manages terminal sessions and command execution"""

    def __init__(self):
        """Initialize terminal manager"""
        self.sessions: Dict[str, TerminalSession] = {}
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.output_streamers: Dict[str, OutputStreamer] = {}
        logger.info("TerminalManager initialized successfully")

    async def create_session(
        self, user_id: str, config: Optional[TerminalConfig] = None
    ) -> TerminalSession:
        """
        Create a new terminal session

        Args:
            user_id: User ID
            config: Optional terminal configuration

        Returns:
            TerminalSession object
        """
        session_id = str(uuid.uuid4())

        if config is None:
            config = TerminalConfig()

        session = TerminalSession(
            session_id=session_id,
            user_id=user_id,
            status=TerminalStatus.ACTIVE,
            config=config,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            command_history=[],
            current_directory=config.working_directory,
            environment=config.environment.copy(),
        )

        self.sessions[session_id] = session
        logger.info(f"Terminal session {session_id} created for user {user_id}")

        return session

    async def execute_command(
        self, session_id: str, command: str, stream_output: bool = False
    ) -> CommandExecution:
        """
        Execute a command in a terminal session

        Args:
            session_id: Session ID
            command: Command to execute
            stream_output: Enable real-time output streaming

        Returns:
            CommandExecution object with results
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.status == TerminalStatus.CLOSED:
            raise ValueError(f"Session {session_id} is closed")

        command_id = str(uuid.uuid4())
        started_at = datetime.now()

        execution = CommandExecution(
            command_id=command_id,
            session_id=session_id,
            command=command,
            status=CommandStatus.RUNNING,
            started_at=started_at,
            completed_at=None,
            exit_code=None,
            stdout="",
            stderr="",
            execution_time=None,
        )

        # Update session status
        session.status = TerminalStatus.BUSY
        session.last_activity = datetime.now()

        try:
            # Create output streamer
            streamer = OutputStreamer(max_size=session.config.max_output_size)
            self.output_streamers[command_id] = streamer

            # Handle cd command specially
            if command.strip().startswith("cd "):
                new_dir = command.strip()[3:].strip()
                if new_dir:
                    import os

                    try:
                        # Resolve relative to current directory
                        if not os.path.isabs(new_dir):
                            new_dir = os.path.join(session.current_directory, new_dir)
                        new_dir = os.path.abspath(new_dir)

                        if os.path.isdir(new_dir):
                            session.current_directory = new_dir
                            execution.stdout = f"Changed directory to {new_dir}\n"
                            execution.exit_code = 0
                            execution.status = CommandStatus.COMPLETED
                        else:
                            execution.stderr = f"cd: {new_dir}: No such directory\n"
                            execution.exit_code = 1
                            execution.status = CommandStatus.FAILED
                    except Exception as e:
                        execution.stderr = f"cd: {str(e)}\n"
                        execution.exit_code = 1
                        execution.status = CommandStatus.FAILED
                else:
                    # cd with no args goes to home
                    session.current_directory = session.config.working_directory
                    execution.stdout = (
                        f"Changed directory to {session.current_directory}\n"
                    )
                    execution.exit_code = 0
                    execution.status = CommandStatus.COMPLETED

                execution.completed_at = datetime.now()
                execution.execution_time = (
                    execution.completed_at - started_at
                ).total_seconds()

            # Handle export command
            elif command.strip().startswith("export "):
                try:
                    # Parse export command
                    export_str = command.strip()[7:].strip()
                    if "=" in export_str:
                        key, value = export_str.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        session.environment[key] = value
                        execution.stdout = f"Exported {key}={value}\n"
                        execution.exit_code = 0
                        execution.status = CommandStatus.COMPLETED
                    else:
                        execution.stderr = "export: invalid syntax\n"
                        execution.exit_code = 1
                        execution.status = CommandStatus.FAILED
                except Exception as e:
                    execution.stderr = f"export: {str(e)}\n"
                    execution.exit_code = 1
                    execution.status = CommandStatus.FAILED

                execution.completed_at = datetime.now()
                execution.execution_time = (
                    execution.completed_at - started_at
                ).total_seconds()

            # Execute regular command
            else:
                # Prepare environment
                env = session.environment.copy()

                # Execute command
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=session.current_directory,
                    env=env,
                    text=True,
                )

                self.active_processes[command_id] = process

                # Read output
                stdout, stderr = process.communicate(timeout=session.config.timeout)

                # Store output
                streamer.add_stdout(stdout)
                streamer.add_stderr(stderr)

                execution.stdout = streamer.get_stdout()
                execution.stderr = streamer.get_stderr()
                execution.exit_code = process.returncode
                execution.status = (
                    CommandStatus.COMPLETED
                    if process.returncode == 0
                    else CommandStatus.FAILED
                )
                execution.completed_at = datetime.now()
                execution.execution_time = (
                    execution.completed_at - started_at
                ).total_seconds()

                # Cleanup
                if command_id in self.active_processes:
                    del self.active_processes[command_id]

        except subprocess.TimeoutExpired:
            execution.status = CommandStatus.FAILED
            execution.stderr = (
                f"Command timed out after {session.config.timeout} seconds\n"
            )
            execution.exit_code = -1
            execution.completed_at = datetime.now()
            execution.execution_time = session.config.timeout

            # Kill process
            if command_id in self.active_processes:
                try:
                    self.active_processes[command_id].kill()
                    del self.active_processes[command_id]
                except:
                    pass

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            execution.status = CommandStatus.FAILED
            execution.stderr = f"Error: {str(e)}\n"
            execution.exit_code = -1
            execution.completed_at = datetime.now()
            execution.execution_time = (datetime.now() - started_at).total_seconds()

        finally:
            # Update session
            session.status = TerminalStatus.ACTIVE
            session.last_activity = datetime.now()

            # Add to history
            if session.config.enable_history:
                session.command_history.append(execution)

                # Trim history if needed
                if len(session.command_history) > session.config.max_history_size:
                    session.command_history = session.command_history[
                        -session.config.max_history_size :
                    ]

            # Cleanup streamer
            if command_id in self.output_streamers:
                del self.output_streamers[command_id]

        return execution

    async def cancel_command(self, command_id: str) -> bool:
        """Cancel a running command"""
        if command_id in self.active_processes:
            try:
                self.active_processes[command_id].kill()
                del self.active_processes[command_id]
                logger.info(f"Command {command_id} cancelled")
                return True
            except Exception as e:
                logger.error(f"Error cancelling command {command_id}: {e}")
                return False
        return False

    async def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get terminal session"""
        return self.sessions.get(session_id)

    async def get_command_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[CommandExecution]:
        """Get command history for a session"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        history = session.command_history
        if limit:
            history = history[-limit:]

        return history

    async def close_session(self, session_id: str) -> bool:
        """Close a terminal session"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Cancel any running commands
        for cmd in session.command_history:
            if cmd.status == CommandStatus.RUNNING:
                await self.cancel_command(cmd.command_id)

        session.status = TerminalStatus.CLOSED
        logger.info(f"Terminal session {session_id} closed")
        return True

    async def list_sessions(
        self, user_id: Optional[str] = None, status: Optional[TerminalStatus] = None
    ) -> List[TerminalSession]:
        """List terminal sessions with optional filtering"""
        sessions = list(self.sessions.values())

        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]

        if status:
            sessions = [s for s in sessions if s.status == status]

        return sessions

    async def cleanup_inactive_sessions(self, max_idle_hours: int = 24) -> int:
        """Cleanup inactive sessions"""
        cutoff_time = datetime.now() - timedelta(hours=max_idle_hours)
        cleaned = 0

        for session_id, session in list(self.sessions.items()):
            if session.last_activity < cutoff_time:
                try:
                    await self.close_session(session_id)
                    del self.sessions[session_id]
                    cleaned += 1
                except Exception as e:
                    logger.error(f"Error cleaning up session {session_id}: {e}")

        logger.info(f"Cleaned up {cleaned} inactive sessions")
        return cleaned


# Global terminal manager instance
_terminal_manager: Optional[TerminalManager] = None


def get_terminal_manager() -> TerminalManager:
    """Get or create global terminal manager instance"""
    global _terminal_manager
    if _terminal_manager is None:
        _terminal_manager = TerminalManager()
    return _terminal_manager
