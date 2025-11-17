"""
iTechSmart HL7 - Message Queue Monitor
Real-time monitoring of HL7 message queues and throughput
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from collections import deque

logger = logging.getLogger(__name__)


class QueueStatus(str, Enum):
    """Queue health status"""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKED = "blocked"


class MessageQueueMetrics(BaseModel):
    """Message queue metrics"""

    queue_name: str
    queue_depth: int
    messages_per_second: float
    messages_per_minute: float
    messages_per_hour: float
    average_processing_time: float  # milliseconds
    oldest_message_age: Optional[float] = None  # seconds
    success_rate: float
    error_rate: float
    status: QueueStatus
    timestamp: datetime


class ThroughputMetrics(BaseModel):
    """Throughput metrics"""

    period: str  # "1min", "5min", "1hour", etc.
    messages_processed: int
    messages_failed: int
    average_rate: float  # messages per second
    peak_rate: float
    timestamp: datetime


class BacklogAlert(BaseModel):
    """Backlog alert"""

    alert_id: str
    queue_name: str
    queue_depth: int
    threshold: int
    oldest_message_age: float
    severity: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None


class MessageQueueMonitor:
    """
    Real-time message queue monitor for HL7 systems

    Features:
    - Real-time throughput tracking
    - Queue depth monitoring
    - Backlog detection and alerting
    - Message age tracking
    - Performance analytics
    - Trend analysis
    - Automatic alert generation
    """

    def __init__(self):
        self.queues: Dict[str, Dict[str, Any]] = {}
        self.metrics_history: Dict[str, deque] = {}
        self.throughput_history: Dict[str, deque] = {}
        self.active_alerts: List[BacklogAlert] = []
        self.alert_history: List[BacklogAlert] = []
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.running = False

        # Configuration
        self.backlog_threshold = 1000  # messages
        self.age_threshold = 300  # 5 minutes
        self.warning_threshold = 500
        self.critical_threshold = 2000

        # Statistics
        self.statistics = {
            "total_messages_processed": 0,
            "total_messages_failed": 0,
            "total_alerts_generated": 0,
            "average_queue_depth": 0,
            "peak_throughput": 0,
        }

    async def start(self):
        """Start the message queue monitor"""
        self.running = True
        logger.info("Message queue monitor started")

        # Start monitoring all registered queues
        for queue_name in self.queues:
            await self._start_monitoring_queue(queue_name)

    async def stop(self):
        """Stop the message queue monitor"""
        self.running = False

        # Stop all monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()

        logger.info("Message queue monitor stopped")

    def register_queue(self, queue_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Register a queue for monitoring

        Args:
            queue_name: Name of the queue
            config: Optional configuration
        """
        self.queues[queue_name] = {
            "config": config or {},
            "message_count": 0,
            "processed_count": 0,
            "failed_count": 0,
            "processing_times": deque(maxlen=1000),
            "message_ages": deque(maxlen=100),
        }

        self.metrics_history[queue_name] = deque(maxlen=1000)
        self.throughput_history[queue_name] = deque(maxlen=1000)

        logger.info(f"Queue registered for monitoring: {queue_name}")

        # Start monitoring if manager is running
        if self.running:
            asyncio.create_task(self._start_monitoring_queue(queue_name))

    async def _start_monitoring_queue(self, queue_name: str):
        """Start monitoring a specific queue"""

        async def monitor():
            while self.running:
                try:
                    # Collect metrics
                    metrics = await self._collect_metrics(queue_name)

                    # Store metrics
                    self.metrics_history[queue_name].append(metrics)

                    # Check for backlog
                    if metrics.queue_depth > self.backlog_threshold:
                        await self._generate_backlog_alert(queue_name, metrics)

                    # Calculate throughput
                    throughput = await self._calculate_throughput(queue_name)
                    self.throughput_history[queue_name].append(throughput)

                    # Wait before next check
                    await asyncio.sleep(10)  # Check every 10 seconds

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error monitoring queue {queue_name}: {str(e)}")
                    await asyncio.sleep(10)

        # Create and store monitoring task
        task = asyncio.create_task(monitor())
        self.monitoring_tasks[queue_name] = task

        logger.info(f"Started monitoring queue: {queue_name}")

    async def _collect_metrics(self, queue_name: str) -> MessageQueueMetrics:
        """Collect metrics for a queue"""
        queue_data = self.queues[queue_name]

        # In production, this would query actual queue systems
        # For now, simulate metrics
        import random

        queue_depth = random.randint(0, 1500)
        processed_count = queue_data["processed_count"]
        failed_count = queue_data["failed_count"]

        # Calculate rates
        messages_per_second = random.uniform(10, 100)
        messages_per_minute = messages_per_second * 60
        messages_per_hour = messages_per_minute * 60

        # Calculate average processing time
        processing_times = list(queue_data["processing_times"])
        avg_processing_time = (
            sum(processing_times) / len(processing_times) if processing_times else 0
        )

        # Calculate oldest message age
        message_ages = list(queue_data["message_ages"])
        oldest_message_age = max(message_ages) if message_ages else None

        # Calculate success rate
        total = processed_count + failed_count
        success_rate = (processed_count / total * 100) if total > 0 else 100
        error_rate = (failed_count / total * 100) if total > 0 else 0

        # Determine status
        if queue_depth > self.critical_threshold:
            status = QueueStatus.CRITICAL
        elif queue_depth > self.warning_threshold:
            status = QueueStatus.WARNING
        else:
            status = QueueStatus.NORMAL

        metrics = MessageQueueMetrics(
            queue_name=queue_name,
            queue_depth=queue_depth,
            messages_per_second=messages_per_second,
            messages_per_minute=messages_per_minute,
            messages_per_hour=messages_per_hour,
            average_processing_time=avg_processing_time,
            oldest_message_age=oldest_message_age,
            success_rate=success_rate,
            error_rate=error_rate,
            status=status,
            timestamp=datetime.now(),
        )

        return metrics

    async def _calculate_throughput(self, queue_name: str) -> ThroughputMetrics:
        """Calculate throughput metrics"""
        queue_data = self.queues[queue_name]

        # Get recent metrics
        recent_metrics = list(self.metrics_history[queue_name])[-60:]  # Last 10 minutes

        if not recent_metrics:
            return ThroughputMetrics(
                period="1min",
                messages_processed=0,
                messages_failed=0,
                average_rate=0,
                peak_rate=0,
                timestamp=datetime.now(),
            )

        # Calculate metrics
        messages_processed = sum(m.messages_per_second for m in recent_metrics)
        average_rate = messages_processed / len(recent_metrics)
        peak_rate = max(m.messages_per_second for m in recent_metrics)

        throughput = ThroughputMetrics(
            period="1min",
            messages_processed=int(messages_processed),
            messages_failed=0,
            average_rate=average_rate,
            peak_rate=peak_rate,
            timestamp=datetime.now(),
        )

        return throughput

    async def _generate_backlog_alert(
        self, queue_name: str, metrics: MessageQueueMetrics
    ):
        """Generate backlog alert"""
        # Check if alert already exists
        existing_alert = next(
            (
                a
                for a in self.active_alerts
                if a.queue_name == queue_name and not a.resolved_at
            ),
            None,
        )

        if existing_alert:
            return  # Alert already active

        # Create new alert
        alert = BacklogAlert(
            alert_id=f"BACKLOG-{queue_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            queue_name=queue_name,
            queue_depth=metrics.queue_depth,
            threshold=self.backlog_threshold,
            oldest_message_age=metrics.oldest_message_age or 0,
            severity=(
                "critical"
                if metrics.queue_depth > self.critical_threshold
                else "warning"
            ),
            detected_at=datetime.now(),
        )

        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        self.statistics["total_alerts_generated"] += 1

        logger.warning(
            f"Backlog alert generated for queue {queue_name}: {metrics.queue_depth} messages"
        )

    def resolve_alert(self, alert_id: str):
        """Resolve an active alert"""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id and not alert.resolved_at:
                alert.resolved_at = datetime.now()
                logger.info(f"Alert {alert_id} resolved")
                return True
        return False

    def record_message_processed(self, queue_name: str, processing_time: float):
        """Record a processed message"""
        if queue_name in self.queues:
            self.queues[queue_name]["processed_count"] += 1
            self.queues[queue_name]["processing_times"].append(processing_time)
            self.statistics["total_messages_processed"] += 1

    def record_message_failed(self, queue_name: str):
        """Record a failed message"""
        if queue_name in self.queues:
            self.queues[queue_name]["failed_count"] += 1
            self.statistics["total_messages_failed"] += 1

    def get_queue_metrics(self, queue_name: str) -> Optional[MessageQueueMetrics]:
        """Get current metrics for a queue"""
        if queue_name not in self.metrics_history:
            return None

        history = self.metrics_history[queue_name]
        return history[-1] if history else None

    def get_all_queue_metrics(self) -> Dict[str, MessageQueueMetrics]:
        """Get current metrics for all queues"""
        metrics = {}
        for queue_name in self.queues:
            metric = self.get_queue_metrics(queue_name)
            if metric:
                metrics[queue_name] = metric
        return metrics

    def get_throughput_metrics(
        self, queue_name: str, period: str = "1min"
    ) -> Optional[ThroughputMetrics]:
        """Get throughput metrics for a queue"""
        if queue_name not in self.throughput_history:
            return None

        history = self.throughput_history[queue_name]
        return history[-1] if history else None

    def get_metrics_history(
        self, queue_name: str, limit: int = 100
    ) -> List[MessageQueueMetrics]:
        """Get metrics history for a queue"""
        if queue_name not in self.metrics_history:
            return []

        history = list(self.metrics_history[queue_name])
        return history[-limit:]

    def get_active_alerts(self) -> List[BacklogAlert]:
        """Get active alerts"""
        return [a for a in self.active_alerts if not a.resolved_at]

    def get_alert_history(self, limit: int = 100) -> List[BacklogAlert]:
        """Get alert history"""
        return self.alert_history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        # Calculate average queue depth
        all_metrics = []
        for history in self.metrics_history.values():
            all_metrics.extend(list(history))

        avg_depth = (
            sum(m.queue_depth for m in all_metrics) / len(all_metrics)
            if all_metrics
            else 0
        )

        # Calculate peak throughput
        all_throughput = []
        for history in self.throughput_history.values():
            all_throughput.extend(list(history))

        peak_throughput = max((t.peak_rate for t in all_throughput), default=0)

        return {
            **self.statistics,
            "average_queue_depth": avg_depth,
            "peak_throughput": peak_throughput,
            "active_alerts": len(self.get_active_alerts()),
            "monitored_queues": len(self.queues),
        }
