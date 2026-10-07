"""
Intelligent Traffic Signal Control System
Main Module: Real-Time Vehicle Density Monitoring and Dynamic Signal Control

This module implements a comprehensive traffic management system that simulates
real-time vehicle density monitoring, dynamic signal timing, and congestion management.

Author: Internship Project Team
Date: 2024
"""

import json
import random
import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SignalState(Enum):
    """Traffic signal states"""
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"


class CongestionLevel(Enum):
    """Traffic congestion levels"""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    SEVERE = "Severe"


class LaneDirection(Enum):
    """Lane directions at intersection"""
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"


@dataclass
class VehicleDensityReading:
    """Data class representing vehicle density reading"""
    lane_id: str
    direction: LaneDirection
    timestamp: datetime.datetime
    vehicle_count: int
    vehicle_density: float  # vehicles per 100m
    average_speed: float  # km/h
    congestion_level: CongestionLevel
    waiting_time: float  # seconds
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'lane_id': self.lane_id,
            'direction': self.direction.value,
            'timestamp': self.timestamp.isoformat(),
            'vehicle_count': self.vehicle_count,
            'vehicle_density': round(self.vehicle_density, 2),
            'average_speed': round(self.average_speed, 2),
            'congestion_level': self.congestion_level.value,
            'waiting_time': round(self.waiting_time, 2)
        }


@dataclass
class SignalTiming:
    """Data class for signal timing configuration"""
    lane_id: str
    direction: LaneDirection
    green_duration: int  # seconds
    yellow_duration: int  # seconds
    red_duration: int  # seconds
    total_cycle_time: int  # seconds
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'lane_id': self.lane_id,
            'direction': self.direction.value,
            'green_duration': self.green_duration,
            'yellow_duration': self.yellow_duration,
            'red_duration': self.red_duration,
            'total_cycle_time': self.total_cycle_time
        }


@dataclass
class TrafficAlert:
    """Data class representing a traffic alert"""
    alert_id: str
    lane_id: str
    alert_type: str  # 'CONGESTION', 'ACCIDENT', 'SIGNAL_MALFUNCTION'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH'
    message: str
    timestamp: datetime.datetime
    resolved: bool = False
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'lane_id': self.lane_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved
        }


class TrafficLane:
    """Class representing a traffic lane at intersection"""
    
    def __init__(self, lane_id: str, direction: LaneDirection, lane_length: float = 500):
        """
        Initialize a traffic lane
        
        Args:
            lane_id: Unique lane identifier
            direction: Direction of traffic (North, South, East, West)
            lane_length: Length of the lane in meters
        """
        self.lane_id = lane_id
        self.direction = direction
        self.lane_length = lane_length
        self.readings: List[VehicleDensityReading] = []
        self.alerts: List[TrafficAlert] = []
        self.current_signal_state = SignalState.RED
        self.signal_timing = None
        self.last_reading = None
        self.total_vehicles_passed = 0
        self.total_waiting_time = 0.0
        
        # Initialize signal timing (default values)
        self._initialize_signal_timing()
    
    def _initialize_signal_timing(self):
        """Initialize default signal timing"""
        self.signal_timing = SignalTiming(
            lane_id=self.lane_id,
            direction=self.direction,
            green_duration=30,
            yellow_duration=3,
            red_duration=33,
            total_cycle_time=66
        )
    
    def take_reading(self, hour_of_day: int = 12, peak_hour: bool = False) -> VehicleDensityReading:
        """
        Take a vehicle density reading
        
        Args:
            hour_of_day: Hour of the day (0-23)
            peak_hour: Whether it's a peak traffic hour
            
        Returns:
            VehicleDensityReading object
        """
        timestamp = datetime.datetime.now()
        
        # Generate vehicle count based on time of day
        if peak_hour or (7 <= hour_of_day < 9) or (17 <= hour_of_day < 19):
            # Peak hours: 7-9 AM and 5-7 PM
            vehicle_count = random.randint(80, 150)
        elif (9 <= hour_of_day < 17):
            # Mid-day: moderate traffic
            vehicle_count = random.randint(40, 80)
        else:
            # Off-peak: light traffic
            vehicle_count = random.randint(10, 40)
        
        # Add some randomness
        vehicle_count += random.randint(-10, 10)
        vehicle_count = max(0, vehicle_count)
        
        # Calculate vehicle density (vehicles per 100m)
        vehicle_density = (vehicle_count / self.lane_length) * 100
        
        # Calculate average speed based on density (inverse relationship)
        if vehicle_density > 80:
            average_speed = random.uniform(5, 15)  # Heavy congestion
        elif vehicle_density > 50:
            average_speed = random.uniform(15, 30)  # Moderate congestion
        elif vehicle_density > 20:
            average_speed = random.uniform(30, 50)  # Light congestion
        else:
            average_speed = random.uniform(50, 80)  # Free flow
        
        # Classify congestion level
        congestion_level = self._classify_congestion(vehicle_density, average_speed)
        
        # Calculate waiting time (inversely proportional to speed)
        if average_speed > 0:
            waiting_time = (self.lane_length / average_speed) * 3.6  # Convert to seconds
        else:
            waiting_time = 300  # 5 minutes max
        
        # Create reading
        reading = VehicleDensityReading(
            lane_id=self.lane_id,
            direction=self.direction,
            timestamp=timestamp,
            vehicle_count=vehicle_count,
            vehicle_density=vehicle_density,
            average_speed=average_speed,
            congestion_level=congestion_level,
            waiting_time=waiting_time
        )
        
        self.readings.append(reading)
        self.last_reading = reading
        self.total_vehicles_passed += vehicle_count
        self.total_waiting_time += waiting_time
        
        # Check for anomalies and generate alerts
        self._detect_anomalies(reading)
        
        return reading
    
    def _classify_congestion(self, density: float, speed: float) -> CongestionLevel:
        """Classify congestion level based on density and speed"""
        if density > 70 or speed < 15:
            return CongestionLevel.SEVERE
        elif density > 50 or speed < 25:
            return CongestionLevel.HIGH
        elif density > 25 or speed < 40:
            return CongestionLevel.MODERATE
        else:
            return CongestionLevel.LOW
    
    def _detect_anomalies(self, reading: VehicleDensityReading):
        """Detect anomalies and generate alerts"""
        if len(self.readings) < 2:
            return
        
        prev_reading = self.readings[-2]
        
        # Check for sudden congestion increase
        density_change = reading.vehicle_density - prev_reading.vehicle_density
        if density_change > 30:  # Sudden increase
            alert = TrafficAlert(
                alert_id=f"ALERT_{len(self.alerts) + 1}",
                lane_id=self.lane_id,
                alert_type="CONGESTION",
                severity="HIGH",
                message=f"Sudden congestion increase: {prev_reading.vehicle_density:.1f} -> {reading.vehicle_density:.1f} vehicles/100m",
                timestamp=datetime.datetime.now()
            )
            self.alerts.append(alert)
            logger.warning(f"Congestion alert at {self.direction.value}: {alert.message}")
        
        # Check for severe congestion
        if reading.congestion_level == CongestionLevel.SEVERE:
            alert = TrafficAlert(
                alert_id=f"ALERT_{len(self.alerts) + 1}",
                lane_id=self.lane_id,
                alert_type="CONGESTION",
                severity="HIGH",
                message=f"Severe congestion detected: Density={reading.vehicle_density:.1f}, Speed={reading.average_speed:.1f}km/h",
                timestamp=datetime.datetime.now()
            )
            self.alerts.append(alert)
            logger.warning(f"Severe congestion at {self.direction.value}")
    
    def adjust_signal_timing(self, vehicle_density: float):
        """
        Dynamically adjust signal timing based on vehicle density
        
        Args:
            vehicle_density: Current vehicle density
        """
        if vehicle_density > 70:
            # Severe congestion: extend green time
            new_green = min(60, 30 + int(vehicle_density / 2))
        elif vehicle_density > 50:
            # High congestion: increase green time
            new_green = min(45, 30 + int(vehicle_density / 5))
        elif vehicle_density > 25:
            # Moderate congestion: normal green time
            new_green = 30
        else:
            # Low traffic: reduce green time
            new_green = max(15, 30 - int((25 - vehicle_density) / 2))
        
        # Update signal timing
        self.signal_timing.green_duration = new_green
        self.signal_timing.red_duration = self.signal_timing.total_cycle_time - new_green - self.signal_timing.yellow_duration
        
        logger.info(f"Signal timing adjusted for {self.direction.value}: Green={new_green}s")
    
    def get_lane_status(self) -> Dict:
        """Get current lane status"""
        return {
            'lane_id': self.lane_id,
            'direction': self.direction.value,
            'current_signal_state': self.current_signal_state.value,
            'last_reading': self.last_reading.to_dict() if self.last_reading else None,
            'signal_timing': self.signal_timing.to_dict() if self.signal_timing else None,
            'total_readings': len(self.readings),
            'active_alerts': len([a for a in self.alerts if not a.resolved]),
            'total_vehicles_passed': self.total_vehicles_passed,
            'average_waiting_time': round(self.total_waiting_time / max(1, len(self.readings)), 2)
        }


class TrafficIntersection:
    """Represents a traffic intersection with multiple lanes"""
    
    def __init__(self, intersection_id: str, intersection_name: str):
        """
        Initialize a traffic intersection
        
        Args:
            intersection_id: Unique intersection identifier
            intersection_name: Name of the intersection
        """
        self.intersection_id = intersection_id
        self.intersection_name = intersection_name
        self.lanes: Dict[str, TrafficLane] = {}
        self.all_alerts: List[TrafficAlert] = []
        self.operation_log: List[Dict] = []
        
        self._initialize_lanes()
        logger.info(f"Traffic intersection '{intersection_name}' initialized with {len(self.lanes)} lanes")
    
    def _initialize_lanes(self):
        """Initialize lanes for all directions"""
        for i, direction in enumerate(LaneDirection):
            lane_id = f"LANE_{direction.value.upper()}_{i+1}"
            lane = TrafficLane(lane_id, direction)
            self.lanes[lane_id] = lane
    
    def read_all_lanes(self, hour_of_day: int = 12, peak_hour: bool = False):
        """Read all lanes in the intersection"""
        for lane_id, lane in self.lanes.items():
            reading = lane.take_reading(hour_of_day, peak_hour)
            
            # Adjust signal timing based on density
            lane.adjust_signal_timing(reading.vehicle_density)
            
            # Collect alerts
            for alert in lane.alerts:
                if not alert.resolved:
                    self.all_alerts.append(alert)
    
    def get_intersection_statistics(self) -> Dict:
        """Get intersection-wide statistics"""
        total_lanes = len(self.lanes)
        
        # Count congestion levels
        congestion_distribution = {}
        for level in CongestionLevel:
            count = sum(1 for lane in self.lanes.values() 
                       if lane.last_reading and lane.last_reading.congestion_level == level)
            congestion_distribution[level.value] = count
        
        # Calculate average metrics
        total_vehicles = sum(lane.last_reading.vehicle_count for lane in self.lanes.values() 
                            if lane.last_reading is not None)
        avg_density = sum(lane.last_reading.vehicle_density for lane in self.lanes.values() 
                         if lane.last_reading is not None) / total_lanes if total_lanes > 0 else 0
        avg_speed = sum(lane.last_reading.average_speed for lane in self.lanes.values() 
                       if lane.last_reading is not None) / total_lanes if total_lanes > 0 else 0
        
        return {
            'total_lanes': total_lanes,
            'total_vehicles': total_vehicles,
            'average_density': round(avg_density, 2),
            'average_speed': round(avg_speed, 2),
            'congestion_distribution': congestion_distribution,
            'active_alerts': len([a for a in self.all_alerts if not a.resolved]),
            'intersection_health_percentage': round(100 - (avg_density / 100) * 100, 2)
        }
    
    def get_hourly_report(self) -> Dict:
        """Generate hourly monitoring report"""
        stats = self.get_intersection_statistics()
        
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'intersection_name': self.intersection_name,
            'statistics': stats
        }
        
        self.operation_log.append({
            'timestamp': datetime.datetime.now().isoformat(),
            'average_density': stats['average_density'],
            'average_speed': stats['average_speed'],
            'active_alerts': stats['active_alerts']
        })
        
        return report
    
    def export_to_json(self, filename: str):
        """Export intersection data to JSON"""
        data = {
            'intersection_name': self.intersection_name,
            'total_lanes': len(self.lanes),
            'lanes': {lane_id: lane.get_lane_status() for lane_id, lane in self.lanes.items()},
            'alerts': [alert.to_dict() for alert in self.all_alerts],
            'operation_log': self.operation_log
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data exported to {filename}")


class TrafficSimulator:
    """Simulator for generating realistic traffic scenarios"""
    
    def __init__(self, intersection: TrafficIntersection):
        """Initialize simulator"""
        self.intersection = intersection
    
    def simulate_24_hour_cycle(self, peak_hours: List[int] = None):
        """
        Simulate a full 24-hour traffic cycle
        
        Args:
            peak_hours: List of hours when peak traffic occurs
        """
        if peak_hours is None:
            peak_hours = [7, 8, 17, 18]  # Morning and evening rush hours
        
        logger.info("Starting 24-hour traffic simulation")
        
        for hour in range(24):
            peak_hour = hour in peak_hours
            
            # Read all lanes
            self.intersection.read_all_lanes(hour_of_day=hour, peak_hour=peak_hour)
            
            # Generate hourly report
            report = self.intersection.get_hourly_report()
            
            logger.info(f"Hour {hour:02d}:00 - Avg Density: {report['statistics']['average_density']:.1f}, "
                       f"Avg Speed: {report['statistics']['average_speed']:.1f}km/h, "
                       f"Alerts: {report['statistics']['active_alerts']}")
        
        logger.info("24-hour simulation completed")
    
    def get_simulation_report(self) -> Dict:
        """Get comprehensive simulation report"""
        return self.intersection.get_hourly_report()


if __name__ == "__main__":
    # Create traffic intersection
    intersection = TrafficIntersection(
        intersection_id="INT_001",
        intersection_name="Main Street & Central Avenue"
    )
    
    # Create simulator
    simulator = TrafficSimulator(intersection)
    
    # Run simulation with peak hours at 7-8 AM and 5-6 PM
    simulator.simulate_24_hour_cycle(peak_hours=[7, 8, 17, 18])
    
    # Generate report
    report = simulator.get_simulation_report()
    
    # Print report
    print("\n" + "="*60)
    print("TRAFFIC SIGNAL CONTROL SYSTEM - SIMULATION REPORT")
    print("="*60)
    print(json.dumps(report, indent=2))
    
    # Export data
    intersection.export_to_json('/home/ubuntu/traffic_intersection_data.json')
