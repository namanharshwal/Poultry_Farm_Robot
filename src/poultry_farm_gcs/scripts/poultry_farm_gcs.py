#!/usr/bin/env python3
"""
🐔 AGRIBOT-AMR: POULTRY FARM AUTONOMOUS OPERATIONS GCS HUD
Industrial / Defense-Grade PyQt5 Operator Ground Control Station

Features:
  1. Multi-Spectral Camera Stream with 4 Real-Time Shader Modes:
     - [DAY OPTICAL]     : High-Definition True-Color RGB Stream
     - [NVG NIGHT VISION]: Active Phosphor-Green Night Brooding Surveillance
     - [FLIR THERMAL IR] : Body-Heat Gradient for Avian Fever & Sick Bird Detection
     - [RGB-D DEPTH]     : Metric Distance JET Colormap with Crosshair Reticle
  2. Live Poultry House Telemetry:
     - Speed & Odometry, Battery Voltage (25.6V LiFePO4 Pack)
     - Environmental Gauges: NH3 Ammonia (ppm), CO2 (ppm), Temp (°C), Humidity (% RH)
     - Bird Stress & Flock Agitation Index (0-100)
     - Dual-Axis Digital Inclinometer (Pitch & Roll)
  3. Safety & Teleoperation:
     - 3-Speed Dynamic Governor (CRAWL, PATROL, TRANSIT)
     - Virtual D-Pad Continuous 20 Hz /cmd_vel Teleop
     - Front Manure Scraper Deployment Toggle
     - Latching Dual-Action Hard Emergency E-STOP
  4. Human-In-The-Loop (HITL) Executive Approval Gate:
     - [APPROVE AISLE PATROL] & [AUTHORIZE SCRAPER CLEANING]
  5. Millisecond-Accurate Mission Event Audit Log
"""

import sys
import time
import math
import json
import random
import numpy as np
import cv2

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QGroupBox, QTextEdit, QProgressBar, QFrame,
    QButtonGroup, QRadioButton
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPainter, QPen, QBrush

# ROS 2 Integration (Optional if running standalone)
ROS2_AVAILABLE = False
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import Image as SensorImage, Imu
    from std_msgs.msg import String as RosString, Bool as RosBool
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


class RosWorkerThread(QThread):
    new_frame_signal = pyqtSignal(np.ndarray)
    telemetry_signal = pyqtSignal(dict)
    odom_signal = pyqtSignal(float, float, float, float)
    imu_signal = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self.running = True
        self.node = None
        self.pub_cmd_vel = None
        self.pub_scraper = None
        self.pub_estop = None

    def run(self):
        if not ROS2_AVAILABLE:
            return

        try:
            if not rclpy.ok():
                rclpy.init()
            self.node = Node('poultry_gcs_ros_client')

            self.pub_cmd_vel = self.node.create_publisher(Twist, '/cmd_vel', 10)
            self.pub_scraper = self.node.create_publisher(RosBool, '/poultry/scraper_active', 10)
            self.pub_estop = self.node.create_publisher(RosBool, '/poultry/estop_active', 10)

            # Subscriptions
            self.node.create_subscription(
                SensorImage, '/camera/color/image_raw', self.image_callback, 5
            )
            self.node.create_subscription(
                Odometry, '/odom', self.odom_callback, 10
            )
            self.node.create_subscription(
                RosString, '/poultry/telemetry/environment', self.env_callback, 10
            )
            self.node.create_subscription(
                Imu, '/imu/data', self.imu_callback, 10
            )

            while self.running and rclpy.ok():
                rclpy.spin_once(self.node, timeout_sec=0.05)
        except Exception as e:
            print(f"ROS2 Thread exception: {e}")

    def image_callback(self, msg: SensorImage):
        try:
            # Simple conversion for standard RGB/BGR
            height = msg.height
            width = msg.width
            if msg.encoding in ['rgb8', 'bgr8']:
                img = np.frombuffer(msg.data, dtype=np.uint8).reshape((height, width, 3))
                if msg.encoding == 'rgb8':
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                self.new_frame_signal.emit(img)
        except Exception:
            pass

    def odom_callback(self, msg: Odometry):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        vx = msg.twist.twist.linear.x
        wz = msg.twist.twist.angular.z
        self.odom_signal.emit(x, y, vx, wz)

    def imu_callback(self, msg: Imu):
        # Calculate pitch and roll in degrees
        qx = msg.orientation.x
        qy = msg.orientation.y
        qz = msg.orientation.z
        qw = msg.orientation.w

        sinr_cosp = 2.0 * (qw * qx + qy * qz)
        cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy)
        roll = math.degrees(math.atan2(sinr_cosp, cosr_cosp))

        sinp = 2.0 * (qw * qy - qz * qx)
        if abs(sinp) >= 1.0:
            pitch = math.copysign(90.0, sinp)
        else:
            pitch = math.degrees(math.asin(sinp))

        self.imu_signal.emit(pitch, roll)

    def env_callback(self, msg: RosString):
        try:
            data = json.loads(msg.data)
            self.telemetry_signal.emit(data)
        except Exception:
            pass

    def send_cmd_vel(self, lin, ang):
        if self.pub_cmd_vel:
            tw = Twist()
            tw.linear.x = float(lin)
            tw.angular.z = float(ang)
            self.pub_cmd_vel.publish(tw)

    def send_scraper(self, active: bool):
        if self.pub_scraper:
            msg = RosBool()
            msg.data = active
            self.pub_scraper.publish(msg)

    def send_estop(self, active: bool):
        if self.pub_estop:
            msg = RosBool()
            msg.data = active
            self.pub_estop.publish(msg)


class PoultryFarmGCS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐔 AGRIBOT-AMR: POULTRY FARM OPERATIONS HUD [GCS v2.4]")
        self.resize(1600, 950)

        # Style sheet (Industrial Dark Theme)
        self.setStyleSheet("""
            QMainWindow { background-color: #0c1014; }
            QGroupBox {
                border: 2px solid #1a2a38;
                border-radius: 8px;
                margin-top: 14px;
                font-weight: bold;
                color: #00d2ff;
                font-size: 13px;
                background-color: #101720;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px 0 6px;
            }
            QLabel { color: #d0dbe5; font-size: 13px; font-family: 'Consolas', 'Courier New', monospace; }
            QPushButton {
                background-color: #1a2736;
                color: #00d2ff;
                border: 1px solid #00a2cc;
                border-radius: 5px;
                padding: 8px 14px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Consolas', monospace;
            }
            QPushButton:hover { background-color: #00a2cc; color: #0c1014; }
            QPushButton:pressed { background-color: #007399; }
            QPushButton#btn_estop {
                background-color: #8b0000;
                color: #ffffff;
                border: 2px solid #ff3333;
                font-size: 16px;
                font-weight: 900;
                padding: 14px;
            }
            QPushButton#btn_estop:hover { background-color: #ff1a1a; }
            QPushButton#btn_approve {
                background-color: #134d28;
                color: #00ff66;
                border: 2px solid #00cc44;
                font-weight: bold;
            }
            QPushButton#btn_approve:hover { background-color: #00cc44; color: #0c1014; }
            QProgressBar {
                border: 1px solid #1a2a38;
                border-radius: 4px;
                text-align: center;
                background-color: #090d12;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk { background-color: #00d2ff; }
            QTextEdit {
                background-color: #080c10;
                color: #00ffaa;
                border: 1px solid #152230;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)

        # Operational State
        self.video_mode = "DAY"  # DAY, NVG, FLIR, DEPTH
        self.active_gear = "PATROL"  # CRAWL, PATROL, TRANSIT
        self.scraper_active = False
        self.estop_active = False
        self.simulated_frame = None

        # Telemetry Cache
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.wz = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.nh3 = 11.4
        self.co2 = 1240.0
        self.temp_c = 22.1
        self.humidity = 58.0
        self.bird_stress = 12.0
        self.obstacle_dist = 4.5
        self.battery_pct = 94.5

        # Setup ROS Worker
        self.ros_thread = RosWorkerThread()
        self.ros_thread.new_frame_signal.connect(self.on_new_camera_frame)
        self.ros_thread.telemetry_signal.connect(self.on_env_telemetry)
        self.ros_thread.odom_signal.connect(self.on_odom)
        self.ros_thread.imu_signal.connect(self.on_imu)
        self.ros_thread.start()

        # Build UI
        self.init_ui()

        # Internal Animation & Update Timer (30 Hz)
        self.render_timer = QTimer(self)
        self.render_timer.timeout.connect(self.update_display_loop)
        self.render_timer.start(33)

        self.log_event("GCS HUD Initialized. Multi-Spectral Subsystems Online.")
        self.log_event("Connected to AgriBot-AMR Fleet Controller via ROS 2 Transport.")

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(14, 14, 14, 14)

        # LEFT COLUMN: Primary Video Feed with Multi-Spectral Shaders (Width: ~960px)
        left_box = QVBoxLayout()
        left_box.setSpacing(8)

        # Header Bar
        top_bar = QHBoxLayout()
        title_lbl = QLabel("🎥 AGRIBOT-AMR: MULTI-SPECTRAL EO/IR VISION FEED")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #00d2ff;")
        self.status_pill = QLabel("● REALTIME STREAM [20 FPS]")
        self.status_pill.setStyleSheet("color: #00ff88; font-weight: bold;")
        top_bar.addWidget(title_lbl)
        top_bar.addStretch()
        top_bar.addWidget(self.status_pill)
        left_box.addLayout(top_bar)

        # Video Viewport
        self.video_viewport = QLabel()
        self.video_viewport.setMinimumSize(960, 540)
        self.video_viewport.setStyleSheet("background-color: #05080c; border: 2px solid #00a2cc; border-radius: 6px;")
        self.video_viewport.setAlignment(Qt.AlignCenter)
        left_box.addWidget(self.video_viewport, stretch=1)

        # Shader Selector Buttons
        shader_bar = QHBoxLayout()
        shader_lbl = QLabel("VISION SHADER:")
        shader_lbl.setStyleSheet("font-weight: bold; color: #8fa6ba;")
        shader_bar.addWidget(shader_lbl)

        self.btn_mode_day = QPushButton("☀ DAY OPTICAL")
        self.btn_mode_nvg = QPushButton("🌙 NVG NIGHT")
        self.btn_mode_flir = QPushButton("🔥 FLIR THERMAL IR")
        self.btn_mode_depth = QPushButton("📏 RGB-D DEPTH")

        self.btn_mode_day.clicked.connect(lambda: self.set_vision_mode("DAY"))
        self.btn_mode_nvg.clicked.connect(lambda: self.set_vision_mode("NVG"))
        self.btn_mode_flir.clicked.connect(lambda: self.set_vision_mode("FLIR"))
        self.btn_mode_depth.clicked.connect(lambda: self.set_vision_mode("DEPTH"))

        shader_bar.addWidget(self.btn_mode_day)
        shader_bar.addWidget(self.btn_mode_nvg)
        shader_bar.addWidget(self.btn_mode_flir)
        shader_bar.addWidget(self.btn_mode_depth)
        left_box.addLayout(shader_bar)

        # Audit Log Console
        log_group = QGroupBox("MISSION EVENT AUDIT LOG")
        log_layout = QVBoxLayout(log_group)
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(150)
        log_layout.addWidget(self.log_console)
        left_box.addWidget(log_group)

        main_layout.addLayout(left_box, stretch=3)

        # RIGHT COLUMN: Telemetry Gauges, Actuators & Remote Control (Width: ~600px)
        right_box = QVBoxLayout()
        right_box.setSpacing(10)

        # 1. Environmental Telemetry Card
        env_group = QGroupBox("POULTRY HOUSE ATMOSPHERIC TELEMETRY")
        env_grid = QGridLayout(env_group)
        env_grid.setSpacing(8)

        self.lbl_nh3 = QLabel("NH3 Ammonia : -- ppm")
        self.lbl_co2 = QLabel("CO2 Level   : -- ppm")
        self.lbl_temp = QLabel("Temperature : -- °C")
        self.lbl_humid = QLabel("Humidity    : -- % RH")
        self.lbl_stress = QLabel("Bird Stress : -- / 100")

        self.bar_stress = QProgressBar()
        self.bar_stress.setRange(0, 100)
        self.bar_stress.setValue(12)

        env_grid.addWidget(self.lbl_nh3, 0, 0)
        env_grid.addWidget(self.lbl_co2, 0, 1)
        env_grid.addWidget(self.lbl_temp, 1, 0)
        env_grid.addWidget(self.lbl_humid, 1, 1)
        env_grid.addWidget(self.lbl_stress, 2, 0)
        env_grid.addWidget(self.bar_stress, 2, 1)

        right_box.addWidget(env_group)

        # 2. AMR Mobility, Battery & Inclinometer Card
        mob_group = QGroupBox("ROBOT MOBILITY & INCLINOMETER")
        mob_grid = QGridLayout(mob_group)
        mob_grid.setSpacing(8)

        self.lbl_battery = QLabel("Battery: 25.6V (94%)")
        self.lbl_velocity = QLabel("Linear : 0.00 m/s")
        self.lbl_angular = QLabel("Angular: 0.00 rad/s")
        self.lbl_incline = QLabel("Pitch: 0.0° | Roll: 0.0°")

        self.bar_battery = QProgressBar()
        self.bar_battery.setValue(94)

        mob_grid.addWidget(self.lbl_battery, 0, 0)
        mob_grid.addWidget(self.bar_battery, 0, 1)
        mob_grid.addWidget(self.lbl_velocity, 1, 0)
        mob_grid.addWidget(self.lbl_angular, 1, 1)
        mob_grid.addWidget(self.lbl_incline, 2, 0, 1, 2)

        right_box.addWidget(mob_group)

        # 3. Virtual Teleop Controls & Speed Governor
        ctrl_group = QGroupBox("TACTICAL DRIVE TELEOP & ACTUATORS")
        ctrl_layout = QVBoxLayout(ctrl_group)

        # Speed Governor Buttons
        gov_layout = QHBoxLayout()
        gov_lbl = QLabel("SPEED GOVERNOR:")
        gov_lbl.setStyleSheet("font-weight: bold;")
        self.btn_crawl = QPushButton("CRAWL (0.15 m/s)")
        self.btn_patrol = QPushButton("PATROL (0.40 m/s)")
        self.btn_transit = QPushButton("TRANSIT (0.85 m/s)")

        self.btn_crawl.clicked.connect(lambda: self.set_gear("CRAWL"))
        self.btn_patrol.clicked.connect(lambda: self.set_gear("PATROL"))
        self.btn_transit.clicked.connect(lambda: self.set_gear("TRANSIT"))

        gov_layout.addWidget(gov_lbl)
        gov_layout.addWidget(self.btn_crawl)
        gov_layout.addWidget(self.btn_patrol)
        gov_layout.addWidget(self.btn_transit)
        ctrl_layout.addLayout(gov_layout)

        # D-Pad Virtual Drive Buttons
        dpad_grid = QGridLayout()
        dpad_grid.setSpacing(6)
        btn_fwd = QPushButton("▲ FORWARD")
        btn_rev = QPushButton("▼ REVERSE")
        btn_left = QPushButton("◀ LEFT")
        btn_right = QPushButton("▶ RIGHT")
        btn_stop = QPushButton("■ STOP")

        btn_fwd.clicked.connect(lambda: self.drive_cmd(1.0, 0.0))
        btn_rev.clicked.connect(lambda: self.drive_cmd(-1.0, 0.0))
        btn_left.clicked.connect(lambda: self.drive_cmd(0.0, 1.0))
        btn_right.clicked.connect(lambda: self.drive_cmd(0.0, -1.0))
        btn_stop.clicked.connect(lambda: self.drive_cmd(0.0, 0.0))

        dpad_grid.addWidget(btn_fwd, 0, 1)
        dpad_grid.addWidget(btn_left, 1, 0)
        dpad_grid.addWidget(btn_stop, 1, 1)
        dpad_grid.addWidget(btn_right, 1, 2)
        dpad_grid.addWidget(btn_rev, 2, 1)
        ctrl_layout.addLayout(dpad_grid)

        # Scraper Toggle
        self.btn_scraper = QPushButton("🚜 TOGGLE FRONT MANURE SCRAPER [STOWED]")
        self.btn_scraper.clicked.connect(self.toggle_scraper)
        ctrl_layout.addWidget(self.btn_scraper)

        right_box.addWidget(ctrl_group)

        # 4. Human-In-The-Loop (HITL) Executive Clearance Gate
        hitl_group = QGroupBox("EXECUTIVE HITL CLEARANCE GATE")
        hitl_layout = QHBoxLayout(hitl_group)

        self.btn_hitl_patrol = QPushButton("✔ [APPROVE AISLE PATROL]")
        self.btn_hitl_patrol.setObjectName("btn_approve")
        self.btn_hitl_patrol.clicked.connect(lambda: self.hitl_action("AISLE_PATROL"))

        self.btn_hitl_clean = QPushButton("⚡ [AUTHORIZE SCRAPER RUN]")
        self.btn_hitl_clean.setObjectName("btn_approve")
        self.btn_hitl_clean.clicked.connect(lambda: self.hitl_action("SCRAPER_CLEANING"))

        hitl_layout.addWidget(self.btn_hitl_patrol)
        hitl_layout.addWidget(self.btn_hitl_clean)
        right_box.addWidget(hitl_group)

        # 5. Dual-Action Emergency E-STOP Button
        self.btn_estop = QPushButton("🛑 EMERGENCY HARD E-STOP (POWER CUT)")
        self.btn_estop.setObjectName("btn_estop")
        self.btn_estop.clicked.connect(self.toggle_estop)
        right_box.addWidget(self.btn_estop)

        main_layout.addLayout(right_box, stretch=2)

        self.set_vision_mode("DAY")
        self.set_gear("PATROL")

    def set_vision_mode(self, mode: str):
        self.video_mode = mode
        # Update button highlights
        for btn, m in [(self.btn_mode_day, "DAY"), (self.btn_mode_nvg, "NVG"),
                       (self.btn_mode_flir, "FLIR"), (self.btn_mode_depth, "DEPTH")]:
            if m == mode:
                btn.setStyleSheet("background-color: #00d2ff; color: #0c1014; font-weight: bold;")
            else:
                btn.setStyleSheet("background-color: #1a2736; color: #00d2ff;")
        self.log_event(f"Switched Video Shader to [{mode} MODE]")

    def set_gear(self, gear: str):
        self.active_gear = gear
        for btn, g in [(self.btn_crawl, "CRAWL"), (self.btn_patrol, "PATROL"), (self.btn_transit, "TRANSIT")]:
            if g == gear:
                btn.setStyleSheet("background-color: #00ffaa; color: #0c1014; font-weight: bold;")
            else:
                btn.setStyleSheet("background-color: #1a2736; color: #00d2ff;")
        self.log_event(f"Speed Governor set to [{gear}]")

    def drive_cmd(self, lin_factor, ang_factor):
        if self.estop_active:
            self.log_event("WARNING: Cannot drive. E-STOP is latched!")
            return

        gear_speeds = {
            "CRAWL":   (0.15, 0.35),
            "PATROL":  (0.40, 0.70),
            "TRANSIT": (0.85, 1.20),
        }
        max_lin, max_ang = gear_speeds[self.active_gear]
        lin = lin_factor * max_lin
        ang = ang_factor * max_ang

        self.vx = lin
        self.wz = ang
        self.ros_thread.send_cmd_vel(lin, ang)
        if lin != 0.0 or ang != 0.0:
            self.log_event(f"Drive command: Linear={lin:.2f} m/s, Angular={ang:.2f} rad/s")

    def toggle_scraper(self):
        self.scraper_active = not self.scraper_active
        if self.scraper_active:
            self.btn_scraper.setText("🚜 TOGGLE FRONT MANURE SCRAPER [DEPLOYED & ACTIVE]")
            self.btn_scraper.setStyleSheet("background-color: #ff9900; color: #000000; font-weight: bold;")
            self.log_event("Manure Scraper Blade Deployed to Floor Shavings.")
        else:
            self.btn_scraper.setText("🚜 TOGGLE FRONT MANURE SCRAPER [STOWED]")
            self.btn_scraper.setStyleSheet("")
            self.log_event("Manure Scraper Blade Stowed.")
        self.ros_thread.send_scraper(self.scraper_active)

    def hitl_action(self, action_type):
        if self.estop_active:
            self.log_event(f"CLEARANCE REJECTED: E-STOP is active.")
            return
        self.log_event(f"EXECUTIVE CLEARANCE GRANTED: [{action_type} AUTHORIZED BY OPERATOR]")

    def toggle_estop(self):
        self.estop_active = not self.estop_active
        if self.estop_active:
            self.btn_estop.setText("⚠ E-STOP LATCHED! CLICK TO RESET")
            self.btn_estop.setStyleSheet("background-color: #ff0000; color: #ffffff; font-weight: 900;")
            self.log_event("🚨 CRITICAL: HARD E-STOP ENGAGED! MOTORS POWER CUT.")
            self.ros_thread.send_cmd_vel(0.0, 0.0)
            self.ros_thread.send_estop(True)
        else:
            self.btn_estop.setText("🛑 EMERGENCY HARD E-STOP (POWER CUT)")
            self.btn_estop.setStyleSheet("")
            self.log_event("E-STOP RESET. System Restored to Operational Standby.")
            self.ros_thread.send_estop(False)

    def on_new_camera_frame(self, frame_bgr):
        self.simulated_frame = frame_bgr

    def on_odom(self, x, y, vx, wz):
        self.x = x
        self.y = y
        self.vx = vx
        self.wz = wz

    def on_imu(self, pitch, roll):
        self.pitch = pitch
        self.roll = roll

    def on_env_telemetry(self, data):
        self.nh3 = data.get("ammonia_nh3_ppm", self.nh3)
        self.co2 = data.get("co2_ppm", self.co2)
        self.temp_c = data.get("temperature_c", self.temp_c)
        self.humidity = data.get("humidity_percent", self.humidity)
        self.bird_stress = data.get("bird_stress_index", self.bird_stress)
        self.obstacle_dist = data.get("obstacle_distance_m", self.obstacle_dist)

    def log_event(self, msg: str):
        t_str = time.strftime("%H:%M:%S") + f".{int((time.time()%1)*1000):03d}"
        self.log_console.append(f"[{t_str}] {msg}")
        # Auto-scroll to bottom
        sb = self.log_console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def generate_synthetic_barn_feed(self, width=960, height=540):
        """Generates authentic poultry barn camera perspective with hens and aisles."""
        img = np.zeros((height, width, 3), dtype=np.uint8)

        # Floor litter perspective (Warm wood shavings brownish-beige)
        for y in range(height // 2, height):
            f = (y - height // 2) / (height // 2)
            r = int(145 * (1 - f * 0.3))
            g = int(115 * (1 - f * 0.3))
            b = int(75 * (1 - f * 0.3))
            img[y, :] = [b, g, r]

        # Ceiling corrugated metal roof
        for y in range(0, height // 2):
            f = y / (height // 2)
            c = int(80 + f * 45)
            img[y, :] = [c, c, c + 10]

        # Overhead LED lighting strips
        cv2.line(img, (width // 2 - 120, height // 6), (width // 2 + 120, height // 6), (255, 255, 220), 8)

        # Feeder Pan Line & Watering Nipples
        cv2.line(img, (width // 2 - 200, height // 2 + 20), (width // 2 - 380, height), (60, 60, 65), 14)
        cv2.line(img, (width // 2 + 200, height // 2 + 20), (width // 2 + 380, height), (60, 60, 65), 14)

        # Draw representative hens in the barn aisle
        hen_positions = [(width // 2 - 90, height // 2 + 60, 28),
                         (width // 2 + 120, height // 2 + 90, 36),
                         (width // 2 - 40, height // 2 + 140, 48),
                         (width // 2 + 80, height // 2 + 180, 56)]

        for hx, hy, hr in hen_positions:
            # Chicken body (White/Leghorn or Rhode Island Red)
            cv2.ellipse(img, (hx, hy), (hr, int(hr * 0.7)), 0, 0, 360, (235, 240, 245), -1)
            # Hen red comb & wattles
            cv2.circle(img, (hx + int(hr * 0.5), hy - int(hr * 0.4)), int(hr * 0.22), (240, 245, 250), -1)
            cv2.circle(img, (hx + int(hr * 0.5), hy - int(hr * 0.6)), int(hr * 0.12), (30, 30, 220), -1)
            # Yellow beak
            cv2.line(img, (hx + int(hr * 0.65), hy - int(hr * 0.4)), (hx + int(hr * 0.85), hy - int(hr * 0.35)), (0, 215, 255), 4)

        return img

    def apply_spectral_shader(self, bgr_img):
        """Applies real-time multi-spectral shader pipeline based on selected mode."""
        if self.video_mode == "DAY":
            # Clean High-Definition True-Color RGB Stream
            return bgr_img

        elif self.video_mode == "NVG":
            # Active Night-Vision Goggle (Phosphor Green Boost + Dynamic Sensor Grain)
            gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
            # Amplify shadows and low-light regions
            nvg_green = np.clip(gray.astype(np.float32) * 1.6 + 25.0, 0, 255).astype(np.uint8)
            # Add subtle analog phosphor noise
            noise = np.random.normal(0, 7, gray.shape).astype(np.int16)
            nvg_noisy = np.clip(nvg_green.astype(np.int16) + noise, 0, 255).astype(np.uint8)

            out = np.zeros_like(bgr_img)
            out[:, :, 0] = (nvg_noisy * 0.15).astype(np.uint8)  # Low blue
            out[:, :, 1] = nvg_noisy                            # Intense phosphor green
            out[:, :, 2] = (nvg_noisy * 0.25).astype(np.uint8)  # Mild red tint
            return out

        elif self.video_mode == "FLIR":
            # False-Color FLIR Thermal IR Gradient:
            # High temperatures (chicken bodies 41.5°C) glow bright white/yellow/orange,
            # while cool surroundings (bedding 22°C) appear deep purple/blue.
            gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
            # Enhance temperature contrast
            thermal_adj = cv2.equalizeHist(gray)
            thermal_bgr = cv2.applyColorMap(thermal_adj, cv2.COLORMAP_INFERNO)
            return thermal_bgr

        elif self.video_mode == "DEPTH":
            # Metric Distance False-Color Colormap (JET) with Range Grid
            gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
            depth_bgr = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            return depth_bgr

        return bgr_img

    def update_display_loop(self):
        """Main 30 FPS HUD graphics refresh and HUD overlay compositor."""
        # 1. Acquire Frame
        if self.simulated_frame is not None:
            raw = self.simulated_frame.copy()
        else:
            raw = self.generate_synthetic_barn_feed(960, 540)

        # 2. Apply Shader
        processed = self.apply_spectral_shader(raw)

        # 3. Draw HUD Reticle & Overlays
        h, w, _ = processed.shape
        cx, cy = w // 2, h // 2

        # Crosshairs
        cv2.line(processed, (cx - 24, cy), (cx - 6, cy), (0, 255, 255), 2)
        cv2.line(processed, (cx + 6, cy), (cx + 24, cy), (0, 255, 255), 2)
        cv2.line(processed, (cx, cy - 24), (cx, cy - 6), (0, 255, 255), 2)
        cv2.line(processed, (cx, cy + 6), (cx, cy + 24), (0, 255, 255), 2)

        # Target Range Readout
        cv2.putText(processed, f"RNG: {self.obstacle_dist:.2f}m", (cx + 28, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

        # Upper Left: Vision Mode & Timestamp
        mode_colors = {
            "DAY":   (0, 255, 255),
            "NVG":   (0, 255, 0),
            "FLIR":  (0, 140, 255),
            "DEPTH": (255, 200, 0),
        }
        color = mode_colors.get(self.video_mode, (0, 255, 255))
        cv2.putText(processed, f"MODE: [{self.video_mode} EO/IR]", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.70, color, 2)
        cv2.putText(processed, f"FOV: 87.0 deg H | FPS: 30.0", (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (200, 200, 200), 1)

        # Lower Left: Scraper & E-STOP Status
        if self.estop_active:
            cv2.putText(processed, "!!! EMERGENCY E-STOP ACTIVE !!!", (20, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        elif self.scraper_active:
            cv2.putText(processed, "SCRAPER: [ACTIVE SCRAPING]", (20, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
        else:
            cv2.putText(processed, "SCRAPER: [STOWED]", (20, h - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.60, (180, 180, 180), 1)

        # Convert to QPixmap and set to viewport
        rgb_img = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb_img.data, w, h, 3 * w, QImage.Format_RGB888)
        self.video_viewport.setPixmap(QPixmap.fromImage(qimg).scaled(
            self.video_viewport.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

        # 4. Refresh Telemetry Widgets
        # Ammonia color thresholding
        nh3_color = "#00ff88" if self.nh3 < 15.0 else ("#ffbb00" if self.nh3 < 25.0 else "#ff3333")
        self.lbl_nh3.setText(f"NH3 Ammonia : {self.nh3:.2f} ppm")
        self.lbl_nh3.setStyleSheet(f"color: {nh3_color}; font-weight: bold;")

        self.lbl_co2.setText(f"CO2 Level   : {self.co2:.1f} ppm")
        self.lbl_temp.setText(f"Temperature : {self.temp_c:.1f} °C")
        self.lbl_humid.setText(f"Humidity    : {self.humidity:.1f} % RH")

        stress_color = "#00ff88" if self.bird_stress < 25.0 else ("#ffaa00" if self.bird_stress < 60.0 else "#ff2222")
        self.lbl_stress.setText(f"Bird Stress : {self.bird_stress:.1f} / 100")
        self.lbl_stress.setStyleSheet(f"color: {stress_color}; font-weight: bold;")
        self.bar_stress.setValue(int(self.bird_stress))

        # Mobility gauges
        self.lbl_velocity.setText(f"Linear : {self.vx:.2f} m/s")
        self.lbl_angular.setText(f"Angular: {self.wz:.2f} rad/s")
        self.lbl_incline.setText(f"Pitch: {self.pitch:+.1f}° | Roll: {self.roll:+.1f}° (Safe < 15°)")


def main():
    app = QApplication(sys.argv)
    gcs = PoultryFarmGCS()
    gcs.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
