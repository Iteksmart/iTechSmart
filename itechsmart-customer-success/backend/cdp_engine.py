"""
iTechSmart Customer Data Platform (CDP) Engine
Real-time customer profile unification, journey orchestration, and personalization
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
import asyncpg
from kafka import KafkaConsumer, KafkaProducer
from neo4j import GraphDatabase
import redis
import pandas as pd
import numpy as np

from app.crm_integrations.manager import CRMIntegrationManager
from app.crm_integrations.base_crm import CRMContact
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    PURCHASE = "purchase"
    FORM_SUBMIT = "form_submit"
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    APP_OPEN = "app_open"
    SUPPORT_TICKET = "support_ticket"
    CHURN_RISK = "churn_risk"

@dataclass
class CustomerProfile:
    customer_id: str
    unified_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    lifetime_value: float = 0.0
    health_score: float = 50.0
    churn_risk: float = 0.0
    segment_ids: List[str] = None
    attributes: Dict[str, Any] = None

@dataclass
class CustomerEvent:
    event_id: str
    customer_id: str
    event_type: EventType
    timestamp: datetime
    channel: str
    properties: Dict[str, Any]
    device_id: Optional[str] = None
    session_id: Optional[str] = None

class CDPEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_pool = None
        self.redis_client = None
        self.neo4j_driver = None
        self.kafka_producer = None
        self.kafka_consumer = None
        self.crm_manager = None
        
    async def initialize(self):
        """Initialize all connections and services"""
        try:
            # Database connections
            self.db_pool = await asyncpg.create_pool(
                self.config['database_url'],
                min_size=5,
                max_size=20
            )
            
            # Redis for caching
            self.redis_client = redis.Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                decode_responses=True
            )
            
            # Neo4j for identity graph
            self.neo4j_driver = GraphDatabase.driver(
                self.config['neo4j_uri'],
                auth=(self.config['neo4j_user'], self.config['neo4j_password'])
            )
            
            # Kafka for event streaming
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=self.config['kafka_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            self.kafka_consumer = KafkaConsumer(
                'customer_events',
                bootstrap_servers=self.config['kafka_servers'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            logger.info("CDP Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CDP Engine: {e}")
            raise

    async def process_event(self, event_data: Dict[str, Any]) -> bool:
        """Process incoming customer event"""
        try:
            event = CustomerEvent(
                event_id=event_data['event_id'],
                customer_id=event_data['customer_id'],
                event_type=EventType(event_data['event_type']),
                timestamp=datetime.fromisoformat(event_data['timestamp']),
                channel=event_data['channel'],
                properties=event_data['properties'],
                device_id=event_data.get('device_id'),
                session_id=event_data.get('session_id')
            )
            
            # Store event in database
            await self._store_event(event)
            
            # Update customer profile
            await self._update_customer_profile(event)
            
            # Update identity graph
            await self._update_identity_graph(event)
            
            # Trigger real-time actions
            await self._trigger_realtime_actions(event)
            
            # Publish to Kafka for downstream processing
            await self._publish_event(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing event {event_data.get('event_id')}: {e}")
            return False

    async def get_unified_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """Get unified customer profile"""
        try:
            # Check cache first
            cache_key = f"profile:{customer_id}"
            cached_profile = self.redis_client.get(cache_key)
            
            if cached_profile:
                return CustomerProfile(**json.loads(cached_profile))
            
            # Fetch from database
            query = """
                SELECT * FROM customer_profiles 
                WHERE customer_id = $1 OR unified_id = $1
            """
            
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(query, customer_id)
                
            if row:
                profile = CustomerProfile(
                    customer_id=row['customer_id'],
                    unified_id=row['unified_id'],
                    email=row['email'],
                    phone=row['phone'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    company=row['company'],
                    created_at=row['created_at'],
                    last_updated=row['last_updated'],
                    lifetime_value=float(row['lifetime_value']),
                    health_score=float(row['health_score']),
                    churn_risk=float(row['churn_risk']),
                    segment_ids=row.get('segment_ids', []),
                    attributes=row.get('attributes', {})
                )
                
                # Cache for 5 minutes
                self.redis_client.setex(
                    cache_key, 
                    300, 
                    json.dumps(asdict(profile), default=str)
                )
                
                return profile
                
            return None
            
        except Exception as e:
            logger.error(f"Error fetching profile for {customer_id}: {e}")
            return None

    async def resolve_identity(self, identifiers: Dict[str, str]) -> str:
        """Resolve customer identity across multiple identifiers"""
        try:
            with self.neo4j_driver.session() as session:
                result = session.run("""
                    MATCH (c:Customer)
                    WHERE ANY(id IN $identifiers.keys() 
                             WHERE c[id] = $identifiers[id])
                    RETURN c.unified_id as unified_id
                """, identifiers=identifiers)
                
                record = result.single()
                if record:
                    return record['unified_id']
                
                # Create new unified identity
                unified_id = f"unified_{datetime.now().timestamp()}"
                session.run("""
                    CREATE (c:Customer {
                        unified_id: $unified_id,
                        created_at: datetime()
                    })
                """, unified_id=unified_id)
                
                # Link identifiers
                for key, value in identifiers.items():
                    session.run("""
                        MATCH (c:Customer {unified_id: $unified_id})
                        SET c[$key] = $value
                    """, unified_id=unified_id, key=key, value=value)
                
                return unified_id
                
        except Exception as e:
            logger.error(f"Error resolving identity: {e}")
            return None

    async def create_customer_segment(self, 
                                    name: str,
                                    criteria: Dict[str, Any],
                                    description: str = None) -> str:
        """Create dynamic customer segment"""
        try:
            segment_id = f"seg_{datetime.now().timestamp()}"
            
            # Store segment definition
            query = """
                INSERT INTO customer_segments 
                (segment_id, name, criteria, description, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query, 
                    segment_id, 
                    name, 
                    json.dumps(criteria), 
                    description, 
                    datetime.now()
                )
            
            # Calculate initial segment membership
            await self._update_segment_membership(segment_id, criteria)
            
            return segment_id
            
        except Exception as e:
            logger.error(f"Error creating segment {name}: {e}")
            return None

    async def get_journey_analytics(self, 
                                  customer_id: str,
                                  days_back: int = 30) -> Dict[str, Any]:
        """Get customer journey analytics"""
        try:
            start_date = datetime.now() - timedelta(days=days_back)
            
            query = """
                SELECT 
                    event_type,
                    channel,
                    COUNT(*) as event_count,
                    AVG(extract(epoch FROM (next_event.timestamp - timestamp))) as avg_time_to_next
                FROM customer_events
                WHERE customer_id = $1 AND timestamp >= $2
                LEFT JOIN LATERAL (
                    SELECT timestamp FROM customer_events ce2 
                    WHERE ce2.customer_id = customer_events.customer_id 
                    AND ce2.timestamp > customer_events.timestamp
                    ORDER BY timestamp ASC LIMIT 1
                ) AS next_event ON true
                GROUP BY event_type, channel
                ORDER BY event_count DESC
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query, customer_id, start_date)
            
            analytics = {
                'customer_id': customer_id,
                'period_days': days_back,
                'total_events': sum(row['event_count'] for row in rows),
                'unique_channels': len(set(row['channel'] for row in rows)),
                'event_breakdown': [
                    {
                        'event_type': row['event_type'],
                        'channel': row['channel'],
                        'count': row['event_count'],
                        'avg_time_to_next': float(row['avg_time_to_next']) if row['avg_time_to_next'] else None
                    }
                    for row in rows
                ]
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting journey analytics for {customer_id}: {e}")
            return {}

    async def _store_event(self, event: CustomerEvent):
        """Store event in database"""
        query = """
            INSERT INTO customer_events 
            (event_id, customer_id, event_type, timestamp, channel, 
             properties, device_id, session_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (event_id) DO NOTHING
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                event.event_id,
                event.customer_id,
                event.event_type.value,
                event.timestamp,
                event.channel,
                json.dumps(event.properties),
                event.device_id,
                event.session_id
            )

    async def _update_customer_profile(self, event: CustomerEvent):
        """Update customer profile based on event"""
        profile = await self.get_unified_profile(event.customer_id)
        
        if not profile:
            # Create new profile
            profile = CustomerProfile(
                customer_id=event.customer_id,
                unified_id=event.customer_id,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
        
        # Update last activity
        profile.last_updated = datetime.now()
        
        # Update health score based on event type
        if event.event_type == EventType.PURCHASE:
            profile.health_score = min(100, profile.health_score + 5)
            profile.lifetime_value += event.properties.get('amount', 0)
        elif event.event_type == EventType.SUPPORT_TICKET:
            profile.health_score = max(0, profile.health_score - 2)
        
        # Update in database
        query = """
            INSERT INTO customer_profiles 
            (customer_id, unified_id, email, phone, first_name, last_name,
             company, created_at, last_updated, lifetime_value, 
             health_score, attributes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            ON CONFLICT (customer_id) DO UPDATE SET
                last_updated = EXCLUDED.last_updated,
                lifetime_value = EXCLUDED.lifetime_value,
                health_score = EXCLUDED.health_score,
                attributes = EXCLUDED.attributes
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                profile.customer_id,
                profile.unified_id,
                profile.email,
                profile.phone,
                profile.first_name,
                profile.last_name,
                profile.company,
                profile.created_at,
                profile.last_updated,
                profile.lifetime_value,
                profile.health_score,
                json.dumps(profile.attributes or {})
            )
        
        # Update cache
        cache_key = f"profile:{event.customer_id}"
        self.redis_client.setex(
            cache_key, 
            300, 
            json.dumps(asdict(profile), default=str)
        )

    async def _update_identity_graph(self, event: CustomerEvent):
        """Update identity graph in Neo4j"""
        try:
            with self.neo4j_driver.session() as session:
                # Link device to customer if present
                if event.device_id:
                    session.run("""
                        MATCH (c:Customer {customer_id: $customer_id})
                        MERGE (d:Device {device_id: $device_id})
                        MERGE (c)-[:HAS_DEVICE]->(d)
                        SET d.last_seen = $timestamp
                    """, 
                    customer_id=event.customer_id,
                    device_id=event.device_id,
                    timestamp=event.timestamp
                    )
                
                # Create event node and link to customer
                session.run("""
                    MATCH (c:Customer {customer_id: $customer_id})
                    CREATE (e:Event {
                        event_id: $event_id,
                        type: $event_type,
                        timestamp: $timestamp,
                        channel: $channel
                    })
                    CREATE (c)-[:PERFORMED]->(e)
                """,
                customer_id=event.customer_id,
                event_id=event.event_id,
                event_type=event.event_type.value,
                timestamp=event.timestamp,
                channel=event.channel
                )
                
        except Exception as e:
            logger.error(f"Error updating identity graph: {e}")

    async def _trigger_realtime_actions(self, event: CustomerEvent):
        """Trigger real-time actions based on event"""
        try:
            # Check for churn risk indicators
            if event.event_type == EventType.SUPPORT_TICKET:
                # Check if this is multiple tickets in short time
                recent_tickets = await self._get_recent_events_count(
                    event.customer_id, 
                    EventType.SUPPORT_TICKET, 
                    days=7
                )
                
                if recent_tickets >= 3:
                    await self._trigger_churn_alert(event.customer_id)
            
            # Check for high-value customer actions
            if event.event_type == EventType.PURCHASE:
                amount = event.properties.get('amount', 0)
                if amount > 1000:  # High-value purchase
                    await self._trigger_high_value_alert(event.customer_id, amount)
                    
        except Exception as e:
            logger.error(f"Error triggering realtime actions: {e}")

    async def _publish_event(self, event: CustomerEvent):
        """Publish event to Kafka for downstream processing"""
        try:
            event_data = {
                'event_id': event.event_id,
                'customer_id': event.customer_id,
                'event_type': event.event_type.value,
                'timestamp': event.timestamp.isoformat(),
                'channel': event.channel,
                'properties': event.properties,
                'device_id': event.device_id,
                'session_id': event.session_id
            }
            
            self.kafka_producer.send('customer_events_processed', event_data)
            self.kafka_producer.flush()
            
        except Exception as e:
            logger.error(f"Error publishing event to Kafka: {e}")

    async def _get_recent_events_count(self, 
                                     customer_id: str, 
                                     event_type: EventType, 
                                     days: int = 7) -> int:
        """Get count of recent events for customer"""
        query = """
            SELECT COUNT(*) as count
            FROM customer_events
            WHERE customer_id = $1 
              AND event_type = $2 
              AND timestamp >= NOW() - INTERVAL '%s days'
        """ % days
        
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, customer_id, event_type.value)
            return row['count']

    async def _trigger_churn_alert(self, customer_id: str):
        """Trigger churn risk alert"""
        alert_data = {
            'alert_type': 'churn_risk',
            'customer_id': customer_id,
            'severity': 'high',
            'timestamp': datetime.now().isoformat(),
            'message': f'Customer {customer_id} shows high churn risk indicators'
        }
        
        self.kafka_producer.send('customer_alerts', alert_data)
        self.kafka_producer.flush()

    async def _trigger_high_value_alert(self, customer_id: str, amount: float):
        """Trigger high-value customer alert"""
        alert_data = {
            'alert_type': 'high_value_action',
            'customer_id': customer_id,
            'severity': 'medium',
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'message': f'High-value purchase from customer {customer_id}: ${amount}'
        }
        
        self.kafka_producer.send('customer_alerts', alert_data)
        self.kafka_producer.flush()

    async def _update_segment_membership(self, segment_id: str, criteria: Dict[str, Any]):
        """Update segment membership based on criteria"""
        # This would involve complex SQL queries based on the criteria
        # For now, we'll create a placeholder
        pass

    async def start_event_consumer(self):
        """Start Kafka event consumer"""
        try:
            for message in self.kafka_consumer:
                event_data = message.value
                await self.process_event(event_data)
                
        except Exception as e:
            logger.error(f"Error in event consumer: {e}")

    async def close(self):
        """Close all connections"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            self.redis_client.close()
        if self.neo4j_driver:
            self.neo4j_driver.close()
        if self.kafka_producer:
            self.kafka_producer.close()
        if self.kafka_consumer:
            self.kafka_consumer.close()

# CRM Integration Methods
    async def initialize_crm_integrations(self, crm_configs: Dict[str, Dict[str, Any]]):
        """Initialize CRM integrations"""
        try:
            self.crm_manager = CRMIntegrationManager(crm_configs)
            await self.crm_manager.initialize_connectors()
            logger.info("CRM integrations initialized successfully")
            
            # Perform initial sync
            sync_report = await self.crm_manager.sync_all_crms(incremental=False)
            logger.info(f"Initial CRM sync completed: {sync_report}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CRM integrations: {str(e)}")
            raise

    async def sync_crm_data(self, incremental: bool = True) -> Dict[str, Any]:
        """Sync data from all configured CRM systems"""
        if not self.crm_manager:
            raise ValueError("CRM integrations not initialized")
            
        sync_report = await self.crm_manager.sync_all_crms(incremental=incremental)
        
        # Process synced data into unified profiles
        await self._process_crm_sync_data(sync_report)
        
        return sync_report

    async def _process_crm_sync_data(self, sync_report: Dict[str, Any]):
        """Process CRM sync data and update unified customer profiles"""
        for crm_name, crm_result in sync_report.get('crm_results', {}).items():
            if crm_result.get('status') == 'success':
                # Get unified contacts from this CRM
                contacts = await self.crm_manager.get_unified_contacts()
                
                for contact_data in contacts:
                    # Convert to CustomerProfile and merge
                    profile = await self._convert_crm_contact_to_profile(contact_data)
                    await self.unify_profile(profile)

    async def _convert_crm_contact_to_profile(self, contact_data: Dict[str, Any]) -> CustomerProfile:
        """Convert CRM contact data to CustomerProfile"""
        return CustomerProfile(
            customer_id=contact_data.get('id', ''),
            unified_id=f"crm_{contact_data.get('source_system', '')}_{contact_data.get('id', '')}",
            email=contact_data.get('email'),
            phone=contact_data.get('phone'),
            first_name=contact_data.get('first_name'),
            last_name=contact_data.get('last_name'),
            company=contact_data.get('company'),
            lead_score=contact_data.get('lead_score'),
            source_system=contact_data.get('source_system'),
            created_date=contact_data.get('created_date'),
            last_updated=contact_data.get('last_updated')
        )

    async def get_crm_contacts(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get unified contacts from all CRM systems"""
        if not self.crm_manager:
            raise ValueError("CRM integrations not initialized")
            
        return await self.crm_manager.get_unified_contacts(filters)

    async def create_crm_contact(self, contact: CRMContact) -> Dict[str, Optional[str]]:
        """Create contact in all configured CRM systems"""
        if not self.crm_manager:
            raise ValueError("CRM integrations not initialized")
            
        return await self.crm_manager.create_contact_in_all_crms(contact)

    async def update_crm_contact(self, contact_id: str, data: Dict[str, Any]) -> Dict[str, bool]:
        """Update contact in all CRM systems"""
        if not self.crm_manager:
            raise ValueError("CRM integrations not initialized")
            
        return await self.crm_manager.update_contact_in_all_crms(contact_id, data)

    async def get_crm_sync_status(self) -> Dict[str, Any]:
        """Get current CRM sync status"""
        if not self.crm_manager:
            return {'status': 'not_initialized'}
            
        return await self.crm_manager.get_sync_status()

    async def test_crm_connections(self) -> Dict[str, bool]:
        """Test connections to all CRM systems"""
        if not self.crm_manager:
            raise ValueError("CRM integrations not initialized")
            
        return await self.crm_manager.test_all_connections()

# Configuration and initialization
async def main():
    config = {
        'database_url': 'postgresql://user:pass@localhost/itechsmart_cdp',
        'redis_host': 'localhost',
        'redis_port': 6379,
        'neo4j_uri': 'bolt://localhost:7687',
        'neo4j_user': 'neo4j',
        'neo4j_password': 'password',
        'kafka_servers': ['localhost:9092'],
        'crm_integrations': {
            'salesforce': {
                'client_id': 'your_salesforce_client_id',
                'client_secret': 'your_salesforce_client_secret',
                'username': 'your_salesforce_username',
                'password': 'your_salesforce_password'
            },
            'hubspot': {
                'access_token': 'your_hubspot_access_token'
            },
            'marketo': {
                'endpoint': 'your_marketo_endpoint',
                'client_id': 'your_marketo_client_id',
                'client_secret': 'your_marketo_client_secret'
            }
        }
    }
    
    cdp_engine = CDPEngine(config)
    await cdp_engine.initialize()
    
    # Initialize CRM integrations
    await cdp_engine.initialize_crm_integrations(config.get('crm_integrations', {}))
    
    # Start event consumer in background
    consumer_task = asyncio.create_task(cdp_engine.start_event_consumer())
    
    try:
        # Keep the service running
        await asyncio.gather(consumer_task)
    except KeyboardInterrupt:
        logger.info("Shutting down CDP Engine...")
    finally:
        await cdp_engine.close()

if __name__ == "__main__":
    asyncio.run(main())