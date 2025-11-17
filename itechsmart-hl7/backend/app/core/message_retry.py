"""
iTechSmart HL7 - Automatic Message Retry System
Handles failed HL7 message delivery with intelligent retry logic
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import hashlib

logger = logging.getLogger(__name__)


class MessageStatus(str, Enum):
    """Message delivery status"""

    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"
    QUARANTINED = "quarantined"


class RetryStrategy(str, Enum):
    """Retry strategy types"""

    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_INTERVAL = "fixed_interval"
    CUSTOM = "custom"


class HL7Message(BaseModel):
    """HL7 message model"""

    message_id: str
    message_type: str  # ADT, ORM, ORU, etc.
    content: str
    source_system: str
    destination_system: str
    priority: int = 5  # 1-10, 10 is highest
    created_at: datetime
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    next_retry_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class RetryPolicy(BaseModel):
    """Retry policy configuration"""

    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_retries: int = 3
    initial_delay: int = 60  # seconds
    max_delay: int = 3600  # 1 hour
    backoff_multiplier: float = 2.0
    retry_on_errors: List[str] = [
        "connection_timeout",
        "connection_refused",
        "network_error",
        "temporary_failure",
    ]
    dead_letter_on_errors: List[str] = [
        "invalid_message",
        "authentication_failed",
        "authorization_failed",
    ]


class MessageRetrySystem:
    """
    Automatic message retry system for HL7 messages

    Features:
    - Intelligent retry with exponential backoff
    - Priority-based retry queue
    - Dead letter queue for permanent failures
    - Message quarantine for malformed messages
    - Retry history and analytics
    - Configurable retry policies
    """

    def __init__(self, retry_policy: Optional[RetryPolicy] = None):
        self.retry_policy = retry_policy or RetryPolicy()
        self.retry_queue: List[HL7Message] = []
        self.dead_letter_queue: List[HL7Message] = []
        self.quarantine_queue: List[HL7Message] = []
        self.processing_messages: Dict[str, HL7Message] = {}
        self.delivered_messages: List[HL7Message] = []
        self.statistics = {
            "total_messages": 0,
            "delivered": 0,
            "failed": 0,
            "retrying": 0,
            "dead_letter": 0,
            "quarantined": 0,
            "average_retry_count": 0,
            "average_delivery_time": 0,
        }
        self.running = False

    async def start(self):
        """Start the retry system"""
        self.running = True
        logger.info("Message retry system started")

        # Start background retry processor
        asyncio.create_task(self._process_retry_queue())

    async def stop(self):
        """Stop the retry system"""
        self.running = False
        logger.info("Message retry system stopped")

    async def submit_message(self, message: HL7Message) -> str:
        """
        Submit a message for delivery

        Args:
            message: HL7Message to deliver

        Returns:
            Message ID
        """
        try:
            # Generate message ID if not provided
            if not message.message_id:
                message.message_id = self._generate_message_id(message)

            # Add to retry queue
            self.retry_queue.append(message)
            self.statistics["total_messages"] += 1

            logger.info(f"Message {message.message_id} submitted for delivery")

            return message.message_id

        except Exception as e:
            logger.error(f"Error submitting message: {str(e)}")
            raise

    def _generate_message_id(self, message: HL7Message) -> str:
        """Generate unique message ID"""
        content_hash = hashlib.md5(message.content.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"HL7-{timestamp}-{content_hash}"

    async def _process_retry_queue(self):
        """Background processor for retry queue"""
        while self.running:
            try:
                # Sort by priority and next retry time
                self.retry_queue.sort(
                    key=lambda m: (-m.priority, m.next_retry_at or datetime.now())
                )

                # Process messages ready for retry
                now = datetime.now()
                messages_to_process = [
                    m
                    for m in self.retry_queue
                    if m.next_retry_at is None or m.next_retry_at <= now
                ]

                for message in messages_to_process[:10]:  # Process up to 10 at a time
                    await self._process_message(message)

                # Wait before next iteration
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error in retry queue processor: {str(e)}")
                await asyncio.sleep(10)

    async def _process_message(self, message: HL7Message):
        """Process a single message"""
        try:
            # Remove from retry queue
            if message in self.retry_queue:
                self.retry_queue.remove(message)

            # Mark as processing
            message.status = MessageStatus.PROCESSING
            self.processing_messages[message.message_id] = message

            # Attempt delivery
            success = await self._attempt_delivery(message)

            if success:
                await self._handle_success(message)
            else:
                await self._handle_failure(message)

        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {str(e)}")
            message.last_error = str(e)
            await self._handle_failure(message)
        finally:
            # Remove from processing
            if message.message_id in self.processing_messages:
                del self.processing_messages[message.message_id]

    async def _attempt_delivery(self, message: HL7Message) -> bool:
        """
        Attempt to deliver message

        Args:
            message: HL7Message to deliver

        Returns:
            True if delivered successfully, False otherwise
        """
        try:
            logger.info(
                f"Attempting delivery of message {message.message_id} (attempt {message.retry_count + 1})"
            )

            # In production, this would actually send the message
            # For now, simulate delivery
            await asyncio.sleep(1)

            # Simulate 80% success rate
            import random

            success = random.random() < 0.8

            if success:
                logger.info(f"Message {message.message_id} delivered successfully")
                return True
            else:
                message.last_error = "Simulated delivery failure"
                logger.warning(f"Message {message.message_id} delivery failed")
                return False

        except Exception as e:
            message.last_error = str(e)
            logger.error(f"Error delivering message {message.message_id}: {str(e)}")
            return False

    async def _handle_success(self, message: HL7Message):
        """Handle successful message delivery"""
        message.status = MessageStatus.DELIVERED
        message.delivered_at = datetime.now()

        # Add to delivered messages
        self.delivered_messages.append(message)

        # Update statistics
        self.statistics["delivered"] += 1

        # Calculate delivery time
        delivery_time = (message.delivered_at - message.created_at).total_seconds()
        self._update_average_delivery_time(delivery_time)

        logger.info(
            f"Message {message.message_id} delivered successfully after {message.retry_count} retries"
        )

    async def _handle_failure(self, message: HL7Message):
        """Handle message delivery failure"""
        message.retry_count += 1

        # Check if should retry
        if self._should_retry(message):
            await self._schedule_retry(message)
        else:
            await self._move_to_dead_letter(message)

    def _should_retry(self, message: HL7Message) -> bool:
        """Determine if message should be retried"""
        # Check max retries
        if message.retry_count >= message.max_retries:
            return False

        # Check if error is retryable
        if message.last_error:
            for error in self.retry_policy.dead_letter_on_errors:
                if error in message.last_error.lower():
                    return False

        return True

    async def _schedule_retry(self, message: HL7Message):
        """Schedule message for retry"""
        message.status = MessageStatus.RETRYING

        # Calculate next retry time based on strategy
        delay = self._calculate_retry_delay(message)
        message.next_retry_at = datetime.now() + timedelta(seconds=delay)

        # Add back to retry queue
        self.retry_queue.append(message)
        self.statistics["retrying"] += 1

        logger.info(
            f"Message {message.message_id} scheduled for retry in {delay} seconds"
        )

    def _calculate_retry_delay(self, message: HL7Message) -> int:
        """Calculate retry delay based on strategy"""
        if self.retry_policy.strategy == RetryStrategy.IMMEDIATE:
            return 0

        elif self.retry_policy.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.retry_policy.initial_delay * (
                self.retry_policy.backoff_multiplier ** (message.retry_count - 1)
            )
            return min(int(delay), self.retry_policy.max_delay)

        elif self.retry_policy.strategy == RetryStrategy.FIXED_INTERVAL:
            return self.retry_policy.initial_delay

        else:
            return self.retry_policy.initial_delay

    async def _move_to_dead_letter(self, message: HL7Message):
        """Move message to dead letter queue"""
        message.status = MessageStatus.DEAD_LETTER
        self.dead_letter_queue.append(message)
        self.statistics["failed"] += 1
        self.statistics["dead_letter"] += 1

        logger.warning(
            f"Message {message.message_id} moved to dead letter queue after {message.retry_count} retries"
        )

    async def quarantine_message(self, message_id: str, reason: str):
        """Quarantine a message (e.g., malformed)"""
        # Find message
        message = None
        for m in self.retry_queue:
            if m.message_id == message_id:
                message = m
                self.retry_queue.remove(m)
                break

        if message:
            message.status = MessageStatus.QUARANTINED
            message.last_error = reason
            self.quarantine_queue.append(message)
            self.statistics["quarantined"] += 1

            logger.warning(f"Message {message_id} quarantined: {reason}")

    async def retry_dead_letter_message(self, message_id: str) -> bool:
        """Manually retry a message from dead letter queue"""
        # Find message in dead letter queue
        message = None
        for m in self.dead_letter_queue:
            if m.message_id == message_id:
                message = m
                self.dead_letter_queue.remove(m)
                break

        if message:
            # Reset retry count and resubmit
            message.retry_count = 0
            message.status = MessageStatus.PENDING
            message.next_retry_at = None
            self.retry_queue.append(message)

            logger.info(
                f"Message {message_id} moved from dead letter queue back to retry queue"
            )
            return True

        return False

    def _update_average_delivery_time(self, delivery_time: float):
        """Update average delivery time statistic"""
        current_avg = self.statistics["average_delivery_time"]
        delivered_count = self.statistics["delivered"]

        new_avg = (
            (current_avg * (delivered_count - 1)) + delivery_time
        ) / delivered_count
        self.statistics["average_delivery_time"] = new_avg

    def get_statistics(self) -> Dict[str, Any]:
        """Get retry system statistics"""
        return {
            **self.statistics,
            "retry_queue_size": len(self.retry_queue),
            "dead_letter_queue_size": len(self.dead_letter_queue),
            "quarantine_queue_size": len(self.quarantine_queue),
            "processing_count": len(self.processing_messages),
        }

    def get_retry_queue(self, limit: int = 100) -> List[HL7Message]:
        """Get messages in retry queue"""
        return self.retry_queue[:limit]

    def get_dead_letter_queue(self, limit: int = 100) -> List[HL7Message]:
        """Get messages in dead letter queue"""
        return self.dead_letter_queue[:limit]

    def get_quarantine_queue(self, limit: int = 100) -> List[HL7Message]:
        """Get messages in quarantine queue"""
        return self.quarantine_queue[:limit]

    def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific message"""
        # Check all queues
        all_messages = (
            self.retry_queue
            + list(self.processing_messages.values())
            + self.delivered_messages
            + self.dead_letter_queue
            + self.quarantine_queue
        )

        for message in all_messages:
            if message.message_id == message_id:
                return {
                    "message_id": message.message_id,
                    "status": message.status,
                    "retry_count": message.retry_count,
                    "last_error": message.last_error,
                    "next_retry_at": (
                        message.next_retry_at.isoformat()
                        if message.next_retry_at
                        else None
                    ),
                    "delivered_at": (
                        message.delivered_at.isoformat()
                        if message.delivered_at
                        else None
                    ),
                }

        return None
