#!/usr/bin/env python3
"""
AgriBot-AMR Autonomous Barn Aisle Inspection & Environmental Monitor:
  - Navigates along pre-programmed floor house & cage battery aisle waypoints
  - Flocks safety slowdown: monitors LiDAR pointcloud or laser scan for hens in path
  - Streams real-time environmental telemetry:
      * NH3 (Ammonia) in ppm
      * CO2 in ppm
      * Air Temperature in °C
      * Relative Humidity in % RH
      * Bird Stress Index (0-100)
"""

import math
import random
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String, Float32, Bool
import json


class PoultryInspectionController(Node):
    def __init__(self):
        super().__init__('poultry_inspection_controller')

        # Subscriptions
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.sub_scan = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.sub_estop = self.create_subscription(Bool, '/poultry/estop_active', self.estop_callback, 10)

        # Publishers
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_env_telemetry = self.create_publisher(String, '/poultry/telemetry/environment', 10)
        self.pub_mission_state = self.create_publisher(String, '/poultry/mission/state', 10)

        # Inspection Waypoints: Barn 1 Floor House (Y=0) and Barn 2 Cage Battery (Y=12)
        # Sequence traverses down Barn 1 aisle, exits into courtyard, enters Barn 2, traverses Barn 2 aisle
        self.waypoints = [
            {"x": -8.0, "y": 0.0, "desc": "Barn 1 Floor House North Aisle Start"},
            {"x":  0.0, "y": 0.0, "desc": "Barn 1 Floor House Midpoint & Feeder Pan Line"},
            {"x":  8.0, "y": 0.0, "desc": "Barn 1 Floor House Rear & Bedding Zone"},
            {"x":  8.0, "y": 6.0, "desc": "Inter-Barn Courtyard Service Road Turn"},
            {"x":  0.0, "y": 6.0, "desc": "Central Logistics Apron Transit"},
            {"x": -8.0, "y": 6.0, "desc": "Courtyard Front Entrance Turn"},
            {"x": -8.0, "y": 12.0, "desc": "Barn 2 Cage Battery Entrance"},
            {"x":  0.0, "y": 12.0, "desc": "Barn 2 Multi-Tier Cage Battery & Egg Conveyor"},
            {"x":  8.0, "y": 12.0, "desc": "Barn 2 Automated Egg Separation Mill & Storage"},
            {"x":  0.0, "y": 6.0, "desc": "Return to Central Charging Station"},
        ]

        self.current_wp_idx = 0
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.obstacle_distance = 10.0
        self.estop_latched = False
        self.autonomous_active = True

        # Control Loop: 10 Hz
        self.timer_control = self.create_timer(0.10, self.control_loop)
        # Environmental Telemetry Stream: 2 Hz
        self.timer_env = self.create_timer(0.50, self.publish_environment_telemetry)

        self.get_logger().info("🐔 Poultry Inspection & Sanitation Controller Initialized.")

    def odom_callback(self, msg: Odometry):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        # Extract yaw from quaternion
        qx = msg.pose.pose.orientation.x
        qy = msg.pose.pose.orientation.y
        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w

        siny_cosp = 2.0 * (qw * qz + qx * qy)
        cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def scan_callback(self, msg: LaserScan):
        # Look ahead within ±30 degrees
        n = len(msg.ranges)
        mid = n // 2
        cone = n // 12
        forward_ranges = [r for r in msg.ranges[mid - cone:mid + cone] if msg.range_min < r < msg.range_max]
        if forward_ranges:
            self.obstacle_distance = min(forward_ranges)
        else:
            self.obstacle_distance = 10.0

    def estop_callback(self, msg: Bool):
        self.estop_latched = msg.data
        if self.estop_latched:
            self.get_logger().warn("E-STOP Active: Halting autonomous inspection.")

    def control_loop(self):
        if not self.autonomous_active or self.estop_latched:
            stop_twist = Twist()
            self.pub_cmd_vel.publish(stop_twist)
            return

        target_wp = self.waypoints[self.current_wp_idx]
        tx = target_wp["x"]
        ty = target_wp["y"]

        dx = tx - self.current_x
        dy = ty - self.current_y
        dist = math.sqrt(dx * dx + dy * dy)

        # Waypoint reached threshold (0.50 m)
        if dist < 0.50:
            self.current_wp_idx = (self.current_wp_idx + 1) % len(self.waypoints)
            self.get_logger().info(f"Waypoint reached! Advancing to: {self.waypoints[self.current_wp_idx]['desc']}")
            return

        target_yaw = math.atan2(dy, dx)
        yaw_error = target_yaw - self.current_yaw

        # Normalize yaw error to [-pi, pi]
        while yaw_error > math.pi:
            yaw_error -= 2.0 * math.pi
        while yaw_error < -math.pi:
            yaw_error += 2.0 * math.pi

        twist = Twist()

        # Flock safety slowdown: if hens or obstacles are detected within 0.8m, slow to crawl
        if self.obstacle_distance < 0.50:
            twist.linear.x = 0.0
            twist.angular.z = 0.35 if yaw_error > 0 else -0.35
        elif self.obstacle_distance < 1.0:
            # Hen-safe crawling speed (0.15 m/s)
            twist.linear.x = 0.15
            twist.angular.z = max(-0.4, min(0.4, 0.8 * yaw_error))
        else:
            # Standard aisle inspection speed (0.35 m/s)
            if abs(yaw_error) > 0.40:
                twist.linear.x = 0.08
                twist.angular.z = max(-0.6, min(0.6, 1.2 * yaw_error))
            else:
                twist.linear.x = 0.35
                twist.angular.z = max(-0.5, min(0.5, 1.0 * yaw_error))

        self.pub_cmd_vel.publish(twist)

        # Publish mission state
        state_msg = String()
        state_msg.data = f"Waypoint [{self.current_wp_idx+1}/{len(self.waypoints)}]: {target_wp['desc']} | Dist: {dist:.2f}m"
        self.pub_mission_state.publish(state_msg)

    def publish_environment_telemetry(self):
        # Realistic poultry house atmospheric simulation
        # In floor house (Y < 6), ammonia is slightly higher due to floor litter
        in_floor_house = abs(self.current_y) < 3.0
        base_nh3 = 14.5 if in_floor_house else 9.2
        nh3 = base_nh3 + random.uniform(-1.2, 1.8)
        co2 = 1250.0 + random.uniform(-60.0, 80.0)
        temp_c = 21.8 + random.uniform(-0.4, 0.5)
        humidity = 58.5 + random.uniform(-2.0, 2.5)

        # Bird stress index (0: Calm, 100: Severe Panic)
        # Proximity to robot slightly raises localized stress index from 8 to ~25
        proximity_factor = max(0.0, 1.0 - (self.obstacle_distance / 2.0))
        bird_stress = 8.0 + proximity_factor * 18.0 + random.uniform(-1.5, 2.0)
        bird_stress = max(0.0, min(100.0, bird_stress))

        payload = {
            "ammonia_nh3_ppm": round(nh3, 2),
            "co2_ppm": round(co2, 1),
            "temperature_c": round(temp_c, 1),
            "humidity_percent": round(humidity, 1),
            "bird_stress_index": round(bird_stress, 1),
            "obstacle_distance_m": round(self.obstacle_distance, 2),
            "manure_scraper_active": True,
            "air_quality_status": "NORMAL" if nh3 < 20.0 else "WARNING_AMMONIA_ELEVATED",
        }

        msg = String()
        msg.data = json.dumps(payload)
        self.pub_env_telemetry.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PoultryInspectionController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
