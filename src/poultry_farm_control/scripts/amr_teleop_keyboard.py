#!/usr/bin/env python3
"""
AgriBot-AMR Poultry Farm Keyboard Teleoperation Console
Features:
  - 3-Speed Dynamic Governor:
      * CRAWL   (0.15 m/s) : Hen-safe brooding speed (prevents scaring flock)
      * PATROL  (0.40 m/s) : Standard aisle inspection & manure scraping
      * TRANSIT (0.85 m/s) : Fast outdoor courtyard & driveway traversal
  - Front Manure Scraper Toggle (Key 'x')
  - Dual-Action Emergency E-STOP (Spacebar)
  - Continuous 20 Hz /cmd_vel streaming
"""

import sys
import select
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, String

BANNER = """
====================================================================
🐔  AGRIBOT-AMR: POULTRY FARM AUTONOMOUS MOBILE ROBOT TELEOP
====================================================================
[DRIVE CONTROLS]
          w : Forward
    a : Left     d : Right
          s : Backward

[SPEED GOVERNOR TOGGLE]
    1 : CRAWL Mode   (0.15 m/s) - Live flock & brooding aisle safety
    2 : PATROL Mode  (0.40 m/s) - Routine inspection & manure scraping
    3 : TRANSIT Mode (0.85 m/s) - Courtyard & paddock fast transit

[ACTUATOR & SAFETY CONTROLS]
    x     : Toggle Front Manure Scraper Blade [DEPLOY / STOW]
    SPACE : EMERGENCY HARD BRAKE (E-STOP)
    q     : Quit Teleop

====================================================================
"""

SETTINGS = [
    {"name": "CRAWL",   "lin": 0.15, "ang": 0.35},
    {"name": "PATROL",  "lin": 0.40, "ang": 0.70},
    {"name": "TRANSIT", "lin": 0.85, "ang": 1.20},
]


def get_key(settings_term):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings_term)
    return key


class PoultryTeleopNode(Node):
    def __init__(self):
        super().__init__('poultry_teleop_keyboard')
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_scraper = self.create_publisher(Bool, '/poultry/scraper_active', 10)
        self.pub_estop = self.create_publisher(Bool, '/poultry/estop_active', 10)

        self.gear_idx = 1  # Default to PATROL
        self.target_lin = 0.0
        self.target_ang = 0.0
        self.scraper_active = False
        self.estop_active = False

        # 20 Hz publishing timer
        self.timer = self.create_timer(0.05, self.timer_callback)

    def timer_callback(self):
        twist = Twist()
        if not self.estop_active:
            twist.linear.x = float(self.target_lin)
            twist.angular.z = float(self.target_ang)
        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.pub_cmd_vel.publish(twist)

        # Decay target velocities smoothly when key released
        self.target_lin *= 0.85
        self.target_ang *= 0.85
        if abs(self.target_lin) < 0.01:
            self.target_lin = 0.0
        if abs(self.target_ang) < 0.01:
            self.target_ang = 0.0


def main(args=None):
    rclpy.init(args=args)
    node = PoultryTeleopNode()
    old_settings = termios.tcgetattr(sys.stdin)

    print(BANNER)

    try:
        while rclpy.ok():
            key = get_key(old_settings)

            if key == 'w':
                node.target_lin = SETTINGS[node.gear_idx]["lin"]
                node.estop_active = False
            elif key == 's':
                node.target_lin = -SETTINGS[node.gear_idx]["lin"]
                node.estop_active = False
            elif key == 'a':
                node.target_ang = SETTINGS[node.gear_idx]["ang"]
                node.estop_active = False
            elif key == 'd':
                node.target_ang = -SETTINGS[node.gear_idx]["ang"]
                node.estop_active = False
            elif key == '1':
                node.gear_idx = 0
                print(f"--> Speed Governor: {SETTINGS[0]['name']} (Max: {SETTINGS[0]['lin']} m/s)")
            elif key == '2':
                node.gear_idx = 1
                print(f"--> Speed Governor: {SETTINGS[1]['name']} (Max: {SETTINGS[1]['lin']} m/s)")
            elif key == '3':
                node.gear_idx = 2
                print(f"--> Speed Governor: {SETTINGS[2]['name']} (Max: {SETTINGS[2]['lin']} m/s)")
            elif key == 'x':
                node.scraper_active = not node.scraper_active
                status = "DEPLOYED (Active Scraping)" if node.scraper_active else "STOWED (Transit)"
                print(f"--> Manure Scraper Blade: {status}")
                msg = Bool()
                msg.data = node.scraper_active
                node.pub_scraper.publish(msg)
            elif key == ' ':
                node.estop_active = True
                node.target_lin = 0.0
                node.target_ang = 0.0
                print("--> 🛑 HARD BRAKE / E-STOP LATCHED!")
                msg = Bool()
                msg.data = True
                node.pub_estop.publish(msg)
            elif key == 'q':
                print("Exiting Teleop...")
                break

            rclpy.spin_once(node, timeout_sec=0.01)

    except Exception as e:
        print(f"Teleop exception: {e}")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        # Send zero velocity before shutdown
        stop_twist = Twist()
        node.pub_cmd_vel.publish(stop_twist)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
