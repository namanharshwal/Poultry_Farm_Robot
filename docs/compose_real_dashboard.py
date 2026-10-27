#!/usr/bin/env python3
import os
import cv2
import numpy as np

IMG_DIR = "/home/nammy/poultry_farm_robot/docs/images"
gazebo_path = os.path.join(IMG_DIR, "real_gazebo_sim_world.png")
gcs_path = os.path.join(IMG_DIR, "real_gcs_hud_live.png")
rviz_path = os.path.join(IMG_DIR, "real_rviz2_perception.png")

gz_img = cv2.imread(gazebo_path)
gcs_img = cv2.imread(gcs_path)
rviz_img = cv2.imread(rviz_path)

W, H = 1920, 1080
canvas = np.zeros((H, W, 3), dtype=np.uint8)
canvas[:] = (12, 15, 20) # Tactical dark background

# Header Bar
cv2.rectangle(canvas, (0, 0), (W, 46), (8, 10, 14), -1)
cv2.putText(canvas, "AGRIBOT-AMR // REAL-TIME POULTRY OPERATIONS & SIMULATION VERIFICATION DASHBOARD", 
            (25, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 220, 255), 2)
cv2.putText(canvas, "LIVE HARDWARE-IN-THE-LOOP (HIL) RUNTIME", 
            (W - 480, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 120), 2)

# Top Left: Real Gazebo Simulation View (1080 x 560)
tl_w, tl_h = 1080, 560
if gz_img is not None:
    # Crop central area of Gazebo view to avoid menu bars if desired, or resize
    gz_crop = gz_img[60:, :]
    gz_resized = cv2.resize(gz_crop, (tl_w, tl_h))
    canvas[60:60+tl_h, 20:20+tl_w] = gz_resized
    cv2.rectangle(canvas, (20, 60), (20+tl_w, 60+tl_h), (40, 55, 75), 2)
    cv2.rectangle(canvas, (20, 60), (20+tl_w, 95), (10, 14, 20), -1)
    cv2.putText(canvas, "1. GAZEBO SIM HARMONIC (8.14.0) // DUAL-THEATER AVIARY FACILITY", (35, 84), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 1)

# Top Right: Real RViz2 Perception Layout (780 x 560)
tr_w, tr_h = 780, 560
if rviz_img is not None:
    rviz_resized = cv2.resize(rviz_img, (tr_w, tr_h))
    canvas[60:60+tr_h, 1120:1120+tr_w] = rviz_resized
    cv2.rectangle(canvas, (1120, 60), (1120+tr_w, 60+tr_h), (40, 55, 75), 2)
    cv2.rectangle(canvas, (1120, 60), (1120+tr_w, 95), (10, 14, 20), -1)
    cv2.putText(canvas, "2. RVIZ2 3D PERCEPTION // POINTCLOUD VOXEL FUSION & TF2 TREE", (1135, 84), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 1)

# Bottom: Real PyQt5 GCS HUD (1880 x 425)
b_w, b_h = 1880, 425
if gcs_img is not None:
    gcs_resized = cv2.resize(gcs_img, (b_w, b_h))
    canvas[635:635+b_h, 20:20+b_w] = gcs_resized
    cv2.rectangle(canvas, (20, 635), (20+b_w, 635+b_h), (40, 55, 75), 2)
    cv2.rectangle(canvas, (20, 635), (20+b_w, 668), (10, 14, 20), -1)
    cv2.putText(canvas, "3. PYQT5 GROUND CONTROL STATION // MULTI-SPECTRAL SHADERS, ATMOSPHERIC GAUGES, HITL GATE & D-PAD", 
                (35, 658), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 1)

out_path = os.path.join(IMG_DIR, "real_mission_composite_dashboard.png")
cv2.imwrite(out_path, canvas)
print("Saved real_mission_composite_dashboard.png successfully!")
