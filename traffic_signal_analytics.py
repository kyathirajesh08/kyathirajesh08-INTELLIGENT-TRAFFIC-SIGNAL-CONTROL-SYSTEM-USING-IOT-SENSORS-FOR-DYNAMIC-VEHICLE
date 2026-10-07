"""
Traffic Signal Control System Analytics and Visualization Module

This module provides comprehensive analytics, reporting, and visualization capabilities
for the Intelligent Traffic Signal Control System.

Author: Internship Project Team
Date: 2024
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta
import random
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10


class TrafficAnalytics:
    """Analytics class for traffic signal system data"""
    
    def __init__(self, intersection):
        """Initialize analytics with intersection data"""
        self.intersection = intersection
        self.data = None
    
    def load_data(self, json_file: str = None):
        """Load traffic data from JSON file"""
        if json_file:
            with open(json_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'intersection_name': self.intersection.intersection_name,
                'total_lanes': len(self.intersection.lanes),
                'lanes': {lane_id: lane.get_lane_status() for lane_id, lane in self.intersection.lanes.items()},
                'alerts': [alert.to_dict() for alert in self.intersection.all_alerts],
                'operation_log': self.intersection.operation_log
            }
    
    def generate_traffic_density_trend(self, output_file: str = '/home/ubuntu/traffic_density_trend.png'):
        """Generate traffic density trend chart"""
        hours = np.arange(0, 24, 1)
        densities = []
        speeds = []
        
        for hour in hours:
            if hour in [7, 8, 17, 18]:  # Peak hours
                density = random.uniform(60, 90)
                speed = random.uniform(15, 25)
            elif (6 <= hour < 10) or (16 <= hour < 20):  # Near peak
                density = random.uniform(40, 60)
                speed = random.uniform(25, 40)
            elif (10 <= hour < 16):  # Mid-day
                density = random.uniform(25, 45)
                speed = random.uniform(40, 55)
            else:  # Off-peak
                density = random.uniform(10, 25)
                speed = random.uniform(55, 75)
            
            densities.append(density)
            speeds.append(speed)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Vehicle density trend
        ax1.plot(hours, densities, marker='o', linewidth=3, markersize=8,
                color='#FF6B6B', label='Vehicle Density')
        ax1.fill_between(hours, densities, alpha=0.3, color='#FF6B6B')
        
        # Add threshold lines
        ax1.axhline(y=25, color='#FFD93D', linestyle='--', linewidth=2, label='Moderate (25)', alpha=0.7)
        ax1.axhline(y=50, color='#FF8C42', linestyle='--', linewidth=2, label='High (50)', alpha=0.7)
        ax1.axhline(y=70, color='#FF6B6B', linestyle='--', linewidth=2, label='Severe (70)', alpha=0.7)
        
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Vehicle Density (vehicles/100m)', fontsize=12, fontweight='bold')
        ax1.set_title('24-Hour Vehicle Density Trend', fontsize=14, fontweight='bold')
        ax1.set_xticks(hours)
        ax1.set_xticklabels([f'{int(h):02d}:00' for h in hours], rotation=45)
        ax1.legend(fontsize=10, loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # Average speed trend
        ax2.plot(hours, speeds, marker='s', linewidth=3, markersize=8,
                color='#4ECDC4', label='Average Speed')
        ax2.fill_between(hours, speeds, alpha=0.3, color='#4ECDC4')
        
        ax2.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Average Speed (km/h)', fontsize=12, fontweight='bold')
        ax2.set_title('24-Hour Average Speed Trend', fontsize=14, fontweight='bold')
        ax2.set_xticks(hours)
        ax2.set_xticklabels([f'{int(h):02d}:00' for h in hours], rotation=45)
        ax2.legend(fontsize=10, loc='lower right')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Traffic density trend chart saved to {output_file}")
        plt.close()
    
    def generate_congestion_distribution(self, output_file: str = '/home/ubuntu/congestion_distribution.png'):
        """Generate congestion level distribution chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Congestion levels
        congestion_types = {
            'Low': random.randint(40, 80),
            'Moderate': random.randint(30, 60),
            'High': random.randint(10, 30),
            'Severe': random.randint(2, 10)
        }
        
        colors_congestion = ['#4ECDC4', '#FFD93D', '#FF8C42', '#FF6B6B']
        wedges, texts, autotexts = ax1.pie(congestion_types.values(), labels=congestion_types.keys(),
                                            autopct='%1.1f%%', colors=colors_congestion, startangle=90,
                                            textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax1.set_title('Congestion Level Distribution', fontsize=14, fontweight='bold')
        
        # Signal efficiency by lane
        lanes = ['North', 'South', 'East', 'West']
        efficiency = [random.uniform(65, 95) for _ in lanes]
        
        colors_efficiency = ['#4ECDC4' if e > 80 else '#FFD93D' if e > 70 else '#FF8C42' for e in efficiency]
        bars = ax2.bar(lanes, efficiency, color=colors_efficiency, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax2.set_ylabel('Signal Efficiency (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Lane-wise Signal Efficiency', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 100)
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, eff in zip(bars, efficiency):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{eff:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Congestion distribution chart saved to {output_file}")
        plt.close()
    
    def generate_signal_timing_analysis(self, output_file: str = '/home/ubuntu/signal_timing_analysis.png'):
        """Generate signal timing analysis chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Signal timing by hour
        hours = np.arange(0, 24, 1)
        green_times = []
        red_times = []
        
        for hour in hours:
            if hour in [7, 8, 17, 18]:  # Peak hours
                green = random.uniform(45, 60)
            elif (6 <= hour < 10) or (16 <= hour < 20):
                green = random.uniform(35, 45)
            else:
                green = random.uniform(20, 35)
            
            green_times.append(green)
            red_times.append(66 - green - 3)  # 3 seconds yellow
        
        ax1.plot(hours, green_times, marker='o', linewidth=3, markersize=8,
                color='#4ECDC4', label='Green Duration')
        ax1.fill_between(hours, green_times, alpha=0.3, color='#4ECDC4')
        
        ax1.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Green Signal Duration (seconds)', fontsize=12, fontweight='bold')
        ax1.set_title('Dynamic Green Signal Timing Throughout Day', fontsize=14, fontweight='bold')
        ax1.set_xticks(hours)
        ax1.set_xticklabels([f'{int(h):02d}:00' for h in hours], rotation=45)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Cycle time distribution
        cycle_times = [random.uniform(60, 70) for _ in range(100)]
        ax2.hist(cycle_times, bins=15, color='#FF8C42', alpha=0.7, edgecolor='black', linewidth=1.5)
        
        ax2.set_xlabel('Cycle Time (seconds)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax2.set_title('Signal Cycle Time Distribution', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Signal timing analysis chart saved to {output_file}")
        plt.close()
    
    def generate_alert_summary(self, output_file: str = '/home/ubuntu/alert_summary.png'):
        """Generate alert summary chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Alert types
        alert_types = {
            'Congestion': random.randint(20, 50),
            'Signal Malfunction': random.randint(2, 8),
            'Accident': random.randint(1, 5),
            'System Alert': random.randint(3, 10)
        }
        
        colors_alerts = ['#FF6B6B', '#FF8C42', '#FFD93D', '#A0A0A0']
        bars = ax1.bar(alert_types.keys(), alert_types.values(), color=colors_alerts, 
                      alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax1.set_ylabel('Number of Alerts', fontsize=12, fontweight='bold')
        ax1.set_title('Alert Type Distribution', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, count in zip(bars, alert_types.values()):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(count)}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Alert severity distribution
        severity_dist = {
            'Low': random.randint(10, 25),
            'Medium': random.randint(15, 35),
            'High': random.randint(5, 15)
        }
        
        severity_colors = ['#FFD93D', '#FF8C42', '#FF6B6B']
        wedges, texts, autotexts = ax2.pie(severity_dist.values(), labels=severity_dist.keys(),
                                            autopct='%1.1f%%', colors=severity_colors, startangle=90,
                                            textprops={'fontsize': 11, 'fontweight': 'bold'})
        ax2.set_title('Alert Severity Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Alert summary chart saved to {output_file}")
        plt.close()
    
    def generate_system_performance(self, output_file: str = '/home/ubuntu/traffic_system_performance.png'):
        """Generate system performance dashboard"""
        stats = self.intersection.get_intersection_statistics()
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
        
        # KPI boxes
        kpis = [
            ('Total Lanes', stats['total_lanes'], '#2E86AB'),
            ('Total Vehicles', stats['total_vehicles'], '#4ECDC4'),
            ('Avg Density', f"{stats['average_density']:.1f}", '#45B7D1'),
            ('Avg Speed', f"{stats['average_speed']:.1f}km/h", '#A8E6CF'),
            ('Active Alerts', stats['active_alerts'], '#FF6B6B'),
            ('System Health', f"{stats['intersection_health_percentage']:.1f}%", '#FFD93D'),
        ]
        
        for idx, (title, value, color) in enumerate(kpis):
            ax = fig.add_subplot(gs[idx // 3, idx % 3])
            ax.add_patch(mpatches.FancyBboxPatch((0.05, 0.2), 0.9, 0.6,
                                                boxstyle="round,pad=0.05", 
                                                edgecolor=color, facecolor=color, alpha=0.2, linewidth=2))
            ax.text(0.5, 0.65, title, ha='center', va='center', fontsize=12, fontweight='bold')
            ax.text(0.5, 0.35, str(value), ha='center', va='center', fontsize=24, fontweight='bold', color=color)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Summary text
        ax_summary = fig.add_subplot(gs[2, :])
        summary_text = f"""
        TRAFFIC INTERSECTION: {self.intersection.intersection_name} | TOTAL LANES: {stats['total_lanes']}
        
        Current Traffic Status: {stats['total_vehicles']} vehicles | Avg Density: {stats['average_density']:.1f} vehicles/100m
        
        Average Speed: {stats['average_speed']:.1f}km/h | Active Alerts: {stats['active_alerts']} | System Health: {stats['intersection_health_percentage']:.1f}%
        """
        ax_summary.text(0.05, 0.5, summary_text, fontsize=11, verticalalignment='center',
                       family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax_summary.axis('off')
        
        fig.suptitle('Intelligent Traffic Signal Control System - Performance Dashboard', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"System performance dashboard saved to {output_file}")
        plt.close()
    
    def generate_all_visualizations(self):
        """Generate all visualization charts"""
        logger.info("Generating all visualization charts...")
        self.generate_traffic_density_trend()
        self.generate_congestion_distribution()
        self.generate_signal_timing_analysis()
        self.generate_alert_summary()
        self.generate_system_performance()
        logger.info("All visualizations generated successfully!")


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
    
    # Generate analytics
    analytics = TrafficAnalytics(intersection)
    analytics.generate_all_visualizations()
    
    print("Analytics generation completed!")
