"""
iTechSmart IoT Fleet Management Platform
Real-time fleet tracking, geospatial analytics, and industrial IoT sensor integration
"""

import asyncio
import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import aiohttp
import asyncpg
import redis
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from shapely.geometry import Point, Polygon
import geopy.distance
from paho.mqtt.client import MQTTClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssetType(Enum):
    VEHICLE = "vehicle"
    CONTAINER = "container"
    EQUIPMENT = "equipment"
    SENSOR = "sensor"
    GATEWAY = "gateway"

class SensorType(Enum):
    GPS = "gps"
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    VIBRATION = "vibration"
    FUEL_LEVEL = "fuel_level"
    OBD_II = "obd_ii"
    CAN_BUS = "can_bus"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Asset:
    asset_id: str
    asset_type: AssetType
    name: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vin: Optional[str] = None
    license_plate: Optional[str] = None
    current_location: Optional[Dict[str, float]] = None
    last_update: Optional[datetime] = None
    status: str = "active"
    health_score: float = 100.0
    utilization_rate: float = 0.0
    fuel_efficiency: float = 0.0
    total_distance: float = 0.0

@dataclass
class SensorReading:
    reading_id: str
    asset_id: str
    sensor_type: SensorType
    timestamp: datetime
    value: float
    unit: str
    metadata: Dict[str, Any] = None

@dataclass
class FleetAlert:
    alert_id: str
    asset_id: str
    alert_type: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False
    metadata: Dict[str, Any] = None

class IoTFleetEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_pool = None
        self.redis_client = None
        self.mqtt_client = None
        self.alert_handlers = {}
        self.prediction_models = {}
        
    async def initialize(self):
        """Initialize all connections and services"""
        try:
            # Database connections
            self.db_pool = await asyncpg.create_pool(
                self.config['database_url'],
                min_size=5,
                max_size=20
            )
            
            # Redis for caching and real-time data
            self.redis_client = redis.Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                decode_responses=True
            )
            
            # MQTT for IoT sensor data
            self.mqtt_client = MQTTClient()
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            await self.mqtt_client.connect(
                self.config['mqtt_host'], 
                self.config['mqtt_port']
            )
            
            # Initialize ML models
            await self._initialize_prediction_models()
            
            logger.info("IoT Fleet Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize IoT Fleet Engine: {e}")
            raise

    async def register_asset(self, asset_data: Dict[str, Any]) -> str:
        """Register new asset in the fleet"""
        try:
            asset = Asset(
                asset_id=asset_data['asset_id'],
                asset_type=AssetType(asset_data['asset_type']),
                name=asset_data['name'],
                make=asset_data.get('make'),
                model=asset_data.get('model'),
                year=asset_data.get('year'),
                vin=asset_data.get('vin'),
                license_plate=asset_data.get('license_plate'),
                current_location=asset_data.get('current_location'),
                last_updated=datetime.now(),
                status=asset_data.get('status', 'active')
            )
            
            # Store in database
            query = """
                INSERT INTO assets 
                (asset_id, asset_type, name, make, model, year, vin, 
                 license_plate, current_location, last_updated, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (asset_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    make = EXCLUDED.make,
                    model = EXCLUDED.model,
                    year = EXCLUDED.year,
                    vin = EXCLUDED.vin,
                    license_plate = EXCLUDED.license_plate,
                    status = EXCLUDED.status,
                    last_updated = EXCLUDED.last_updated
            """
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    asset.asset_id,
                    asset.asset_type.value,
                    asset.name,
                    asset.make,
                    asset.model,
                    asset.year,
                    asset.vin,
                    asset.license_plate,
                    json.dumps(asset.current_location) if asset.current_location else None,
                    asset.last_updated,
                    asset.status
                )
            
            # Cache asset data
            cache_key = f"asset:{asset.asset_id}"
            self.redis_client.setex(
                cache_key, 
                300, 
                json.dumps(asdict(asset), default=str)
            )
            
            logger.info(f"Asset {asset.asset_id} registered successfully")
            return asset.asset_id
            
        except Exception as e:
            logger.error(f"Error registering asset: {e}")
            raise

    async def process_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Process incoming sensor data from IoT devices"""
        try:
            reading = SensorReading(
                reading_id=sensor_data['reading_id'],
                asset_id=sensor_data['asset_id'],
                sensor_type=SensorType(sensor_data['sensor_type']),
                timestamp=datetime.fromisoformat(sensor_data['timestamp']),
                value=float(sensor_data['value']),
                unit=sensor_data['unit'],
                metadata=sensor_data.get('metadata', {})
            )
            
            # Store sensor reading
            await self._store_sensor_reading(reading)
            
            # Update asset status based on sensor data
            await self._update_asset_from_sensor(reading)
            
            # Check for anomalies
            await self._detect_anomalies(reading)
            
            # Predictive maintenance check
            await self._predictive_maintenance_check(reading)
            
            # Update real-time dashboard data
            await self._update_dashboard_data(reading)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
            return False

    async def get_fleet_locations(self) -> List[Dict[str, Any]]:
        """Get real-time locations of all fleet assets"""
        try:
            query = """
                SELECT asset_id, name, asset_type, current_location, 
                       last_updated, status, health_score
                FROM assets 
                WHERE current_location IS NOT NULL
                AND last_updated > NOW() - INTERVAL '1 hour'
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query)
            
            fleet_locations = []
            for row in rows:
                fleet_locations.append({
                    'asset_id': row['asset_id'],
                    'name': row['name'],
                    'type': row['asset_type'],
                    'location': json.loads(row['current_location']) if row['current_location'] else None,
                    'last_updated': row['last_updated'].isoformat(),
                    'status': row['status'],
                    'health_score': float(row['health_score'])
                })
            
            return fleet_locations
            
        except Exception as e:
            logger.error(f"Error getting fleet locations: {e}")
            return []

    async def optimize_routes(self, 
                            start_location: Tuple[float, float],
                            destinations: List[Tuple[float, float]],
                            constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize multi-stop routes using advanced algorithms"""
        try:
            if not destinations:
                return {'optimized_route': [], 'total_distance': 0, 'estimated_time': 0}
            
            # Simple nearest neighbor algorithm (in production, use more sophisticated algorithms)
            unvisited = destinations.copy()
            current_location = start_location
            optimized_route = [current_location]
            total_distance = 0
            
            while unvisited:
                nearest = self._find_nearest_location(current_location, unvisited)
                distance = geopy.distance.geodesic(current_location, nearest).kilometers
                total_distance += distance
                optimized_route.append(nearest)
                unvisited.remove(nearest)
                current_location = nearest
            
            # Estimate time based on average speed (50 km/h for urban, 80 km/h for highway)
            avg_speed = constraints.get('avg_speed', 60) if constraints else 60
            estimated_time = (total_distance / avg_speed) * 60  # minutes
            
            return {
                'optimized_route': optimized_route,
                'total_distance': round(total_distance, 2),
                'estimated_time': round(estimated_time, 2),
                'waypoints': len(destinations)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing routes: {e}")
            return {'error': str(e)}

    async def generate_heatmap_data(self, 
                                  region: Tuple[float, float, float, float],
                                  time_period: int = 24) -> Dict[str, Any]:
        """Generate geospatial heatmap data for fleet activity"""
        try:
            # region = (lat_min, lat_max, lon_min, lon_max)
            lat_min, lat_max, lon_min, lon_max = region
            
            query = """
                SELECT current_location, asset_type
                FROM assets 
                WHERE current_location IS NOT NULL
                AND last_updated > NOW() - INTERVAL '%s hours'
                AND CAST(JSON_EXTRACT(current_location, '$.lat') AS FLOAT) 
                    BETWEEN $2 AND $3
                AND CAST(JSON_EXTRACT(current_location, '$.lon') AS FLOAT) 
                    BETWEEN $4 AND $5
            """ % time_period
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(
                    query, 
                    lat_min, lat_max, lon_min, lon_max
                )
            
            # Create grid cells for heatmap
            grid_size = 0.01  # ~1km grid
            heatmap_data = {}
            
            for row in rows:
                location = json.loads(row['current_location'])
                lat, lon = location['lat'], location['lon']
                
                # Calculate grid cell
                grid_lat = int(lat / grid_size) * grid_size
                grid_lon = int(lon / grid_size) * grid_size
                grid_key = f"{grid_lat:.3f},{grid_lon:.3f}"
                
                if grid_key not in heatmap_data:
                    heatmap_data[grid_key] = {
                        'lat': grid_lat,
                        'lon': grid_lon,
                        'count': 0,
                        'asset_types': {}
                    }
                
                heatmap_data[grid_key]['count'] += 1
                asset_type = row['asset_type']
                heatmap_data[grid_key]['asset_types'][asset_type] = \
                    heatmap_data[grid_key]['asset_types'].get(asset_type, 0) + 1
            
            return {
                'region': region,
                'time_period_hours': time_period,
                'grid_data': list(heatmap_data.values()),
                'total_assets': len(rows),
                'hotspots': sorted(heatmap_data.values(), 
                                 key=lambda x: x['count'], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Error generating heatmap data: {e}")
            return {}

    async def predict_asset_failure(self, asset_id: str) -> Dict[str, Any]:
        """Predict potential asset failure using ML models"""
        try:
            # Get recent sensor data for the asset
            query = """
                SELECT sensor_type, value, timestamp, metadata
                FROM sensor_readings
                WHERE asset_id = $1 
                AND timestamp > NOW() - INTERVAL '7 days'
                ORDER BY timestamp DESC
                LIMIT 1000
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query, asset_id)
            
            if len(rows) < 50:
                return {'prediction': 'insufficient_data', 'confidence': 0.0}
            
            # Prepare data for ML model
            sensor_data = {}
            for row in rows:
                sensor_type = row['sensor_type']
                if sensor_type not in sensor_data:
                    sensor_data[sensor_type] = []
                sensor_data[sensor_type].append({
                    'value': float(row['value']),
                    'timestamp': row['timestamp']
                })
            
            # Extract features
            features = self._extract_failure_features(sensor_data)
            
            # Use pre-trained model (simplified for demo)
            if asset_id in self.prediction_models:
                model = self.prediction_models[asset_id]
                prediction = model.predict([features])[0]
                confidence = max(model.predict_proba([features])[0])
                
                failure_probability = float(prediction)
                
                return {
                    'asset_id': asset_id,
                    'failure_probability': failure_probability,
                    'confidence': confidence,
                    'prediction_date': datetime.now().isoformat(),
                    'recommended_actions': self._get_maintenance_recommendations(
                        failure_probability, features
                    )
                }
            
            return {'prediction': 'model_not_available', 'confidence': 0.0}
            
        except Exception as e:
            logger.error(f"Error predicting asset failure: {e}")
            return {'error': str(e)}

    async def get_fleet_analytics(self) -> Dict[str, Any]:
        """Get comprehensive fleet analytics"""
        try:
            query = """
                SELECT 
                    asset_type,
                    COUNT(*) as total_assets,
                    AVG(health_score) as avg_health_score,
                    AVG(utilization_rate) as avg_utilization,
                    AVG(fuel_efficiency) as avg_fuel_efficiency,
                    SUM(total_distance) as total_distance
                FROM assets
                WHERE status = 'active'
                GROUP BY asset_type
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query)
            
            analytics = {
                'total_assets': sum(row['total_assets'] for row in rows),
                'by_type': [],
                'overall_health': 0,
                'overall_utilization': 0,
                'total_distance': 0
            }
            
            total_weighted_health = 0
            total_weighted_utilization = 0
            
            for row in rows:
                analytics['by_type'].append({
                    'type': row['asset_type'],
                    'count': row['total_assets'],
                    'avg_health_score': float(row['avg_health_score']),
                    'avg_utilization': float(row['avg_utilization']),
                    'avg_fuel_efficiency': float(row['avg_fuel_efficiency']),
                    'total_distance': float(row['total_distance'])
                })
                
                total_weighted_health += row['avg_health_score'] * row['total_assets']
                total_weighted_utilization += row['avg_utilization'] * row['total_assets']
                analytics['total_distance'] += float(row['total_distance'])
            
            if analytics['total_assets'] > 0:
                analytics['overall_health'] = total_weighted_health / analytics['total_assets']
                analytics['overall_utilization'] = total_weighted_utilization / analytics['total_assets']
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting fleet analytics: {e}")
            return {}

    async def _store_sensor_reading(self, reading: SensorReading):
        """Store sensor reading in database"""
        query = """
            INSERT INTO sensor_readings 
            (reading_id, asset_id, sensor_type, timestamp, value, unit, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (reading_id) DO NOTHING
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                reading.reading_id,
                reading.asset_id,
                reading.sensor_type.value,
                reading.timestamp,
                reading.value,
                reading.unit,
                json.dumps(reading.metadata) if reading.metadata else None
            )

    async def _update_asset_from_sensor(self, reading: SensorReading):
        """Update asset status based on sensor data"""
        if reading.sensor_type == SensorType.GPS:
            # Update asset location
            location_data = {
                'lat': reading.metadata.get('lat', reading.value),
                'lon': reading.metadata.get('lon', 0),
                'accuracy': reading.metadata.get('accuracy', 0)
            }
            
            query = """
                UPDATE assets 
                SET current_location = $1, last_updated = $2
                WHERE asset_id = $3
            """
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    json.dumps(location_data),
                    reading.timestamp,
                    reading.asset_id
                )
        
        elif reading.sensor_type == SensorType.FUEL_LEVEL:
            # Update fuel efficiency
            query = """
                UPDATE assets 
                SET fuel_level = $1, last_updated = $2
                WHERE asset_id = $3
            """
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    query,
                    reading.value,
                    reading.timestamp,
                    reading.asset_id
                )

    async def _detect_anomalies(self, reading: SensorReading):
        """Detect anomalies in sensor data"""
        try:
            # Get recent readings for comparison
            query = """
                SELECT value, timestamp
                FROM sensor_readings
                WHERE asset_id = $1 AND sensor_type = $2
                AND timestamp > NOW() - INTERVAL '24 hours'
                ORDER BY timestamp DESC
                LIMIT 100
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(
                    query, 
                    reading.asset_id, 
                    reading.sensor_type.value
                )
            
            if len(rows) < 10:
                return
            
            values = [float(row['value']) for row in rows]
            
            # Simple anomaly detection using standard deviation
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            if abs(reading.value - mean_val) > 3 * std_val:
                # Anomaly detected
                await self._create_alert(
                    asset_id=reading.asset_id,
                    alert_type="sensor_anomaly",
                    severity=AlertSeverity.MEDIUM,
                    message=f"Anomaly detected in {reading.sensor_type.value}: {reading.value} (normal range: {mean_val:.2f} ± {2*std_val:.2f})",
                    metadata={
                        'sensor_type': reading.sensor_type.value,
                        'anomaly_value': reading.value,
                        'normal_range': [mean_val - 2*std_val, mean_val + 2*std_val]
                    }
                )
                
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")

    async def _predictive_maintenance_check(self, reading: SensorReading):
        """Check for predictive maintenance indicators"""
        if reading.sensor_type == SensorType.VIBRATION:
            if reading.value > 8.0:  # High vibration threshold
                await self._create_alert(
                    asset_id=reading.asset_id,
                    alert_type="maintenance_required",
                    severity=AlertSeverity.HIGH,
                    message=f"High vibration detected: {reading.value} - immediate maintenance recommended",
                    metadata={'vibration_level': reading.value}
                )
        
        elif reading.sensor_type == SensorType.TEMPERATURE:
            if reading.value > 90.0:  # High temperature threshold
                await self._create_alert(
                    asset_id=reading.asset_id,
                    alert_type="overheating_risk",
                    severity=AlertSeverity.HIGH,
                    message=f"High temperature detected: {reading.value}°C",
                    metadata={'temperature': reading.value}
                )

    async def _create_alert(self, 
                          asset_id: str,
                          alert_type: str,
                          severity: AlertSeverity,
                          message: str,
                          metadata: Dict[str, Any] = None):
        """Create fleet alert"""
        alert_id = f"alert_{datetime.now().timestamp()}"
        
        alert = FleetAlert(
            alert_id=alert_id,
            asset_id=asset_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        query = """
            INSERT INTO fleet_alerts 
            (alert_id, asset_id, alert_type, severity, message, timestamp, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                query,
                alert.alert_id,
                alert.asset_id,
                alert.alert_type,
                alert.severity.value,
                alert.message,
                alert.timestamp,
                json.dumps(alert.metadata) if alert.metadata else None
            )
        
        # Publish alert to MQTT for real-time notifications
        alert_data = {
            'alert_id': alert.alert_id,
            'asset_id': alert.asset_id,
            'type': alert.alert_type,
            'severity': alert.severity.value,
            'message': alert.message,
            'timestamp': alert.timestamp.isoformat()
        }
        
        await self.mqtt_client.publish('fleet/alerts', json.dumps(alert_data))

    async def _update_dashboard_data(self, reading: SensorReading):
        """Update real-time dashboard data"""
        dashboard_key = f"dashboard:{reading.asset_id}"
        
        # Get current dashboard data
        current_data = self.redis_client.get(dashboard_key)
        if current_data:
            dashboard_data = json.loads(current_data)
        else:
            dashboard_data = {
                'asset_id': reading.asset_id,
                'last_update': None,
                'sensors': {}
            }
        
        # Update with latest reading
        dashboard_data['last_update'] = reading.timestamp.isoformat()
        dashboard_data['sensors'][reading.sensor_type.value] = {
            'value': reading.value,
            'unit': reading.unit,
            'timestamp': reading.timestamp.isoformat()
        }
        
        # Cache for 1 minute
        self.redis_client.setex(dashboard_key, 60, json.dumps(dashboard_data))

    async def _initialize_prediction_models(self):
        """Initialize ML prediction models"""
        # In production, load pre-trained models
        # For demo, create simple models
        self.prediction_models = {
            'demo_model': IsolationForest(contamination=0.1, random_state=42)
        }

    def _find_nearest_location(self, 
                             current: Tuple[float, float], 
                             locations: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Find nearest location from current position"""
        nearest = locations[0]
        min_distance = geopy.distance.geodesic(current, nearest).kilometers
        
        for location in locations[1:]:
            distance = geopy.distance.geodesic(current, location).kilometers
            if distance < min_distance:
                min_distance = distance
                nearest = location
        
        return nearest

    def _extract_failure_features(self, sensor_data: Dict[str, List]) -> List[float]:
        """Extract features for failure prediction"""
        features = []
        
        # Statistical features for each sensor type
        for sensor_type, readings in sensor_data.items():
            if readings:
                values = [r['value'] for r in readings]
                features.extend([
                    np.mean(values),
                    np.std(values),
                    np.max(values),
                    np.min(values)
                ])
            else:
                features.extend([0, 0, 0, 0])
        
        return features

    def _get_maintenance_recommendations(self, 
                                       failure_probability: float, 
                                       features: List[float]) -> List[str]:
        """Get maintenance recommendations based on failure probability"""
        recommendations = []
        
        if failure_probability > 0.8:
            recommendations.extend([
                "Immediate inspection required",
                "Schedule emergency maintenance",
                "Consider temporary asset removal from service"
            ])
        elif failure_probability > 0.6:
            recommendations.extend([
                "Schedule maintenance within 24 hours",
                "Monitor asset closely",
                "Prepare backup equipment"
            ])
        elif failure_probability > 0.4:
            recommendations.extend([
                "Schedule maintenance within 7 days",
                "Increase monitoring frequency"
            ])
        
        return recommendations

    async def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to sensor data topics
            await client.subscribe("sensors/+")
            await client.subscribe("fleet/+")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    async def _on_mqtt_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            if topic.startswith("sensors/"):
                await self.process_sensor_data(payload)
            elif topic.startswith("fleet/"):
                # Handle fleet command messages
                pass
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    async def close(self):
        """Close all connections"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            self.redis_client.close()
        if self.mqtt_client:
            await self.mqtt_client.disconnect()

# Configuration and initialization
async def main():
    config = {
        'database_url': 'postgresql://user:pass@localhost/itechsmart_iot',
        'redis_host': 'localhost',
        'redis_port': 6379,
        'mqtt_host': 'localhost',
        'mqtt_port': 1883
    }
    
    fleet_engine = IoTFleetEngine(config)
    await fleet_engine.initialize()
    
    try:
        # Keep the service running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down IoT Fleet Engine...")
    finally:
        await fleet_engine.close()

if __name__ == "__main__":
    asyncio.run(main())