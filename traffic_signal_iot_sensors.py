"""
IoT Sensor Simulation Module for Traffic Signal Control System

This module simulates IoT-based sensors (vehicle detection, occupancy) used for
intelligent traffic management. It includes sensor data generation, anomaly detection,
and alert generation.

Author: Internship Project Team
Date: 2024
"""

import random
import datetime
import json
import logging
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SensorType(Enum):
    """Types of sensors used in traffic detection"""
    ULTRASONIC = "Ultrasonic"
    CAMERA = "Camera"
    INDUCTIVE_LOOP = "Inductive Loop"
    RADAR = "Radar"


class SensorStatus(Enum):
    """Status of sensor"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    FAULTY = "Faulty"
    MAINTENANCE = "Maintenance"


@dataclass
class VehicleDetectionReading:
    """Data class for vehicle detection reading"""
    sensor_id: str
    timestamp: datetime.datetime
    vehicle_detected: bool
    vehicle_count: int
    occupancy_rate: float  # 0.0 to 1.0
    sensor_type: SensorType
    location: str
    status: SensorStatus
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'sensor_id': self.sensor_id,
            'timestamp': self.timestamp.isoformat(),
            'vehicle_detected': self.vehicle_detected,
            'vehicle_count': self.vehicle_count,
            'occupancy_rate': round(self.occupancy_rate, 3),
            'sensor_type': self.sensor_type.value,
            'location': self.location,
            'status': self.status.value,
            'confidence': round(self.confidence, 3)
        }


@dataclass
class SensorAlert:
    """Data class for sensor alert"""
    alert_id: str
    sensor_id: str
    alert_type: str  # 'MALFUNCTION', 'LOW_CONFIDENCE', 'CALIBRATION_NEEDED'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH'
    message: str
    timestamp: datetime.datetime
    resolved: bool = False
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'sensor_id': self.sensor_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved
        }


class IoTTrafficSensor:
    """Base class for IoT sensors in traffic detection"""
    
    def __init__(self, sensor_id: str, sensor_type: SensorType, location: str):
        """Initialize sensor"""
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location
        self.status = SensorStatus.ACTIVE
        self.last_reading = None
        self.readings_history: List[VehicleDetectionReading] = []
        self.alerts: List[SensorAlert] = []
        self.calibration_needed = False
        self.battery_level = 100.0  # Battery percentage
        self.total_readings = 0
        self.false_positive_rate = 0.0
    
    def take_reading(self, hour_of_day: int = 12, peak_hour: bool = False) -> VehicleDetectionReading:
        """
        Take a vehicle detection reading
        
        Args:
            hour_of_day: Hour of the day (0-23)
            peak_hour: Whether it's a peak traffic hour
            
        Returns:
            VehicleDetectionReading object
        """
        timestamp = datetime.datetime.now()
        
        # Generate vehicle count based on time of day
        if peak_hour or (7 <= hour_of_day < 9) or (17 <= hour_of_day < 19):
            vehicle_count = random.randint(80, 150)
        elif (9 <= hour_of_day < 17):
            vehicle_count = random.randint(40, 80)
        else:
            vehicle_count = random.randint(10, 40)
        
        # Add some randomness
        vehicle_count += random.randint(-10, 10)
        vehicle_count = max(0, vehicle_count)
        
        # Determine if vehicle detected
        vehicle_detected = vehicle_count > 0
        
        # Calculate occupancy rate (0-1)
        occupancy_rate = min(1.0, vehicle_count / 150)
        
        # Calculate confidence based on sensor type and conditions
        confidence = self._calculate_confidence(occupancy_rate)
        
        # Create reading object
        reading = VehicleDetectionReading(
            sensor_id=self.sensor_id,
            timestamp=timestamp,
            vehicle_detected=vehicle_detected,
            vehicle_count=vehicle_count,
            occupancy_rate=occupancy_rate,
            sensor_type=self.sensor_type,
            location=self.location,
            status=self.status,
            confidence=confidence
        )
        
        self.last_reading = reading
        self.readings_history.append(reading)
        self.total_readings += 1
        
        # Simulate battery drain
        self.battery_level -= random.uniform(0.01, 0.03)
        
        # Check for anomalies
        self._check_anomalies(reading)
        
        return reading
    
    def _calculate_confidence(self, occupancy_rate: float) -> float:
        """Calculate confidence score for the reading"""
        base_confidence = 0.95
        
        # Reduce confidence based on sensor type
        if self.sensor_type == SensorType.CAMERA:
            base_confidence = 0.92  # Weather, lighting issues
        elif self.sensor_type == SensorType.ULTRASONIC:
            base_confidence = 0.88  # Noise sensitivity
        elif self.sensor_type == SensorType.RADAR:
            base_confidence = 0.90  # Good in all weather
        
        # Reduce confidence if battery is low
        if self.battery_level < 20:
            base_confidence *= 0.7
        elif self.battery_level < 50:
            base_confidence *= 0.85
        
        # Reduce confidence if sensor needs calibration
        if self.calibration_needed:
            base_confidence *= 0.6
        
        # Reduce confidence if sensor is faulty
        if self.status == SensorStatus.FAULTY:
            base_confidence *= 0.3
        
        return max(0.0, min(1.0, base_confidence))
    
    def _check_anomalies(self, reading: VehicleDetectionReading):
        """Check for sensor anomalies"""
        if len(self.readings_history) < 2:
            return
        
        prev_reading = self.readings_history[-2]
        
        # Check for sudden spikes
        count_change = abs(reading.vehicle_count - prev_reading.vehicle_count)
        
        # Unrealistic change detection
        if count_change > 100:  # More than 100 vehicles in one reading
            alert = SensorAlert(
                alert_id=f"ALERT_{len(self.alerts) + 1}",
                sensor_id=self.sensor_id,
                alert_type="MALFUNCTION",
                severity="MEDIUM",
                message=f"Unrealistic vehicle count spike: {prev_reading.vehicle_count} -> {reading.vehicle_count}",
                timestamp=datetime.datetime.now()
            )
            self.alerts.append(alert)
        
        # Check low confidence
        if reading.confidence < 0.5:
            alert = SensorAlert(
                alert_id=f"ALERT_{len(self.alerts) + 1}",
                sensor_id=self.sensor_id,
                alert_type="LOW_CONFIDENCE",
                severity="MEDIUM",
                message=f"Low reading confidence: {reading.confidence:.2f}",
                timestamp=datetime.datetime.now()
            )
            self.alerts.append(alert)
        
        # Check battery level
        if self.battery_level < 10:
            alert = SensorAlert(
                alert_id=f"ALERT_{len(self.alerts) + 1}",
                sensor_id=self.sensor_id,
                alert_type="MALFUNCTION",
                severity="HIGH",
                message=f"Battery level critical: {self.battery_level:.1f}%",
                timestamp=datetime.datetime.now()
            )
            self.alerts.append(alert)
    
    def calibrate(self):
        """Calibrate sensor"""
        self.calibration_needed = False
        logger.info(f"Sensor {self.sensor_id} calibrated successfully")
    
    def perform_maintenance(self):
        """Perform maintenance on sensor"""
        self.status = SensorStatus.ACTIVE
        self.battery_level = 100.0
        self.calibration_needed = False
        logger.info(f"Maintenance completed for sensor {self.sensor_id}")
    
    def get_health_status(self) -> Dict:
        """Get sensor health status"""
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type.value,
            'location': self.location,
            'status': self.status.value,
            'battery_level': round(self.battery_level, 2),
            'calibration_needed': self.calibration_needed,
            'last_reading': self.last_reading.to_dict() if self.last_reading else None,
            'total_readings': self.total_readings,
            'active_alerts': len([a for a in self.alerts if not a.resolved])
        }


class SensorNetworkTraffic:
    """Network of IoT sensors for the traffic signal system"""
    
    def __init__(self, intersection):
        """Initialize sensor network"""
        self.intersection = intersection
        self.sensors: Dict[str, IoTTrafficSensor] = {}
        self.all_readings: List[VehicleDetectionReading] = []
        self.all_alerts: List[SensorAlert] = []
        
        self._initialize_sensors()
    
    def _initialize_sensors(self):
        """Initialize sensors for all lanes"""
        sensor_types = [SensorType.ULTRASONIC, SensorType.CAMERA, SensorType.INDUCTIVE_LOOP]
        
        for lane_obj in self.intersection.lanes.values():
            location = f"{lane_obj.direction.value} Lane"
            
            # Assign sensor types to each lane
            for i, sensor_type in enumerate(sensor_types):
                sensor_id = f"SENSOR_{lane_obj.lane_id}_{sensor_type.value.replace(' ', '_')}"
                sensor = IoTTrafficSensor(sensor_id, sensor_type, location)
                self.sensors[sensor_id] = sensor
        
        logger.info(f"Initialized {len(self.sensors)} sensors for traffic detection network")
    
    def read_all_sensors(self, hour_of_day: int = 12, peak_hour: bool = False):
        """Read all sensors in the network"""
        for sensor_id, sensor in self.sensors.items():
            # Take reading
            reading = sensor.take_reading(hour_of_day, peak_hour)
            self.all_readings.append(reading)
            
            # Collect alerts
            for alert in sensor.alerts:
                if not alert.resolved:
                    self.all_alerts.append(alert)
    
    def get_network_health(self) -> Dict:
        """Get overall network health"""
        active_sensors = sum(1 for s in self.sensors.values() if s.status == SensorStatus.ACTIVE)
        faulty_sensors = sum(1 for s in self.sensors.values() if s.status == SensorStatus.FAULTY)
        low_battery_sensors = sum(1 for s in self.sensors.values() if s.battery_level < 20)
        
        return {
            'total_sensors': len(self.sensors),
            'active_sensors': active_sensors,
            'faulty_sensors': faulty_sensors,
            'low_battery_sensors': low_battery_sensors,
            'network_health_percentage': round((active_sensors / len(self.sensors)) * 100, 2),
            'total_readings': len(self.all_readings),
            'active_alerts': len([a for a in self.all_alerts if not a.resolved])
        }
    
    def get_sensor_status_report(self) -> Dict:
        """Get detailed sensor status report"""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'network_health': self.get_network_health(),
            'sensor_details': [sensor.get_health_status() for sensor in self.sensors.values()],
            'recent_alerts': [alert.to_dict() for alert in self.all_alerts[-10:]]  # Last 10 alerts
        }
        return report
    
    def export_readings(self, filename: str):
        """Export all sensor readings to JSON"""
        data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_readings': len(self.all_readings),
            'readings': [reading.to_dict() for reading in self.all_readings[-100:]],  # Last 100 readings
            'alerts': [alert.to_dict() for alert in self.all_alerts],
            'network_health': self.get_network_health()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Sensor readings exported to {filename}")


if __name__ == "__main__":
    from traffic_signal_system import TrafficIntersection, TrafficSimulator
    
    # Create intersection
    intersection = TrafficIntersection(
        intersection_id="INT_001",
        intersection_name="Main Street & Central Avenue"
    )
    
    # Run simulation
    simulator = TrafficSimulator(intersection)
    simulator.simulate_24_hour_cycle()
    
    # Create sensor network
    sensor_network = SensorNetworkTraffic(intersection)
    
    # Read all sensors
    for hour in range(24):
        peak_hour = hour in [7, 8, 17, 18]
        sensor_network.read_all_sensors(hour_of_day=hour, peak_hour=peak_hour)
    
    # Get report
    report = sensor_network.get_sensor_status_report()
    print(json.dumps(report, indent=2))
    
    # Export data
    sensor_network.export_readings('/home/ubuntu/traffic_sensor_readings.json')
