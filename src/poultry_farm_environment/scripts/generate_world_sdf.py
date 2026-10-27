#!/usr/bin/env python3
"""
Master World Generator for Dual-Tunnel Poultry Farm with:
  1. Industrial Tunnel Barn 1 (Floor Housing / Broiler & Free-Range).
  2. Industrial Tunnel Barn 2 (5-Tier Colony Layer House with 100 hens).
  3. Industrial Egg Separation & Grading Mill Facility.
  4. Perimeter Security Farm Fencing enclosing the farm complex.
  5. Grand Front Entrance Gate with Roman Serif Named Signboard ("POULTRY FARM").
  6. Poultry Farm Workers in the Outer Garden, Paddock, and Logistics areas.
  7. Lush Natural Shelterbelt / Tree Line (Pine & Oak) planted OUTSIDE the fencing.
  8. Master Ground Plane, Service Roadway, Feed Silos, and Full Egg Distribution.
"""

import os
import math
import random
import numpy as np

BASE_DIR = "/home/nammy/ros2_ws/src/poultry_farm_world"
WORLDS_DIR = os.path.join(BASE_DIR, "worlds")
os.makedirs(WORLDS_DIR, exist_ok=True)


def generate_world_sdf():
    print("--> Generating comprehensive dual-tunnel poultry_farm.sdf with Workers, Fencing, Front Gate Roman Board, and Trees...")

    sdf_lines = []
    w = sdf_lines.append

    w('<?xml version="1.0" ?>')
    w('<sdf version="1.8">')
    w('  <world name="poultry_farm">')
    w('    <!-- Physics Settings -->')
    w('    <physics name="1ms" type="ode">')
    w('      <max_step_size>0.001</max_step_size>')
    w('      <real_time_factor>1.0</real_time_factor>')
    w('      <real_time_update_rate>1000</real_time_update_rate>')
    w('      <ode>')
    w('        <solver><type>quick</type><iters>50</iters><sor>1.3</sor></solver>')
    w('        <constraints><cfm>0.00001</cfm><erp>0.2</erp><contact_max_correcting_vel>100.0</contact_max_correcting_vel><contact_surface_layer>0.001</contact_surface_layer></constraints>')
    w('      </ode>')
    w('    </physics>')
    w('')
    w('    <!-- Gazebo Sim Essential Systems -->')
    w('    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>')
    w('    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>')
    w('    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>')
    w('    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors"><render_engine>ogre2</render_engine></plugin>')
    w('    <plugin filename="gz-sim-contact-system" name="gz::sim::systems::Contact"/>')
    w('')
    w('    <!-- Scene & Atmosphere with Sky and Clouds -->')
    w('    <scene>')
    w('      <ambient>0.68 0.66 0.62 1.0</ambient>')
    w('      <background>0.55 0.75 0.95 1.0</background>')
    w('      <shadows>true</shadows>')
    w('      <grid>false</grid>')
    w('      <sky>')
    w('        <time>12.0</time>')
    w('        <sunrise>6.0</sunrise>')
    w('        <sunset>18.0</sunset>')
    w('        <clouds>')
    w('          <speed>0.8</speed>')
    w('          <direction>1.0 0.0</direction>')
    w('          <humidity>0.6</humidity>')
    w('          <mean_size>0.5</mean_size>')
    w('          <ambient>0.8 0.8 0.8 1.0</ambient>')
    w('        </clouds>')
    w('      </sky>')
    w('    </scene>')
    w('')
    w('    <!-- GUI Camera Configuration with Far Clipping Plane -->')
    w('    <gui fullscreen="0">')
    w('      <camera name="user_camera">')
    w('        <pose>-25.8 8.2 5.1 0 0.12 -0.05</pose>')
    w('        <view_controller>orbit</view_controller>')
    w('        <projection_type>perspective</projection_type>')
    w('        <clip>')
    w('          <near>0.1</near>')
    w('          <far>1000.0</far>')
    w('        </clip>')
    w('      </camera>')
    w('    </gui>')
    w('')
    w('    <!-- Radiant Glowing Sun in the Sky with Clouds -->')
    w('    <include>')
    w('      <name>sun_radiant</name>')
    w('      <uri>model://sun_radiant</uri>')
    w('      <pose>-32.0 54.0 64.0 0 0 0</pose>')
    w('    </include>')
    w('')
    w('    <!-- Natural Directional Sunlight aligned with Radiant Sun -->')
    w('    <light type="directional" name="sun">')
    w('      <cast_shadows>true</cast_shadows>')
    w('      <pose>-32.0 54.0 64.0 0 0 0</pose>')
    w('      <diffuse>0.98 0.95 0.88 1</diffuse>')
    w('      <specular>0.4 0.4 0.4 1</specular>')
    w('      <attenuation><range>1000</range><constant>0.9</constant><linear>0.01</linear><quadratic>0.001</quadratic></attenuation>')
    w('      <direction>0.3714 -0.5571 -0.7428</direction>')
    w('    </light>')
    w('')
    w('    <!-- Spotlight illuminating the Roman Named Signboard at the Front Gate -->')
    w('    <light type="spot" name="entrance_sign_spotlight">')
    w('      <cast_shadows>false</cast_shadows>')
    w('      <pose>-24.5 8.0 5.2 0 0.45 0</pose>')
    w('      <diffuse>1.0 0.96 0.82 1</diffuse>')
    w('      <specular>0.5 0.5 0.4 1</specular>')
    w('      <direction>1.0 0.0 -0.45</direction>')
    w('      <attenuation><range>16.0</range><constant>0.2</constant><linear>0.08</linear><quadratic>0.02</quadratic></attenuation>')
    w('      <spot><inner_angle>0.6</inner_angle><outer_angle>1.1</outer_angle><falloff>1.0</falloff></spot>')
    w('    </light>')
    w('')
    w('    <!-- Interior Lighting: Tunnel Barn 1 (Floor House, Y = 0) -->')
    light_idx = 1
    for lx in [-8.0, -3.0, 3.0, 8.0]:
        for ly in [-2.0, 2.0]:
            w(f'    <light type="point" name="tunnel1_light_{light_idx}">')
            w('      <cast_shadows>false</cast_shadows>')
            w(f'      <pose>{lx} {ly} 3.2 0 0 0</pose>')
            w('      <diffuse>0.85 0.82 0.70 1</diffuse>')
            w('      <specular>0.2 0.2 0.15 1</specular>')
            w('      <attenuation><range>12.0</range><constant>0.2</constant><linear>0.15</linear><quadratic>0.05</quadratic></attenuation>')
            w('    </light>')
            light_idx += 1
    w('')
    w('    <!-- Interior Lighting: Tunnel Barn 2 (5-Tier Layer House, Y = 16) -->')
    light_idx = 1
    for lx in [-8.0, -3.0, 3.0, 8.0]:
        for ly in [14.0, 18.0]:
            w(f'    <light type="point" name="tunnel2_light_{light_idx}">')
            w('      <cast_shadows>false</cast_shadows>')
            w(f'      <pose>{lx} {ly} 3.4 0 0 0</pose>')
            w('      <diffuse>0.90 0.88 0.78 1</diffuse>')
            w('      <specular>0.2 0.2 0.15 1</specular>')
            w('      <attenuation><range>14.0</range><constant>0.2</constant><linear>0.12</linear><quadratic>0.04</quadratic></attenuation>')
            w('    </light>')
            light_idx += 1
    w('')
    w('    <!-- Spot Lighting for Egg Separation Mill Station -->')
    w('    <light type="point" name="egg_mill_spotlight">')
    w('      <cast_shadows>false</cast_shadows>')
    w('      <pose>-9.8 16.0 3.0 0 0 0</pose>')
    w('      <diffuse>1.0 1.0 0.95 1</diffuse>')
    w('      <specular>0.4 0.4 0.4 1</specular>')
    w('      <attenuation><range>8.0</range><constant>0.2</constant><linear>0.1</linear><quadratic>0.03</quadratic></attenuation>')
    w('    </light>')
    w('')
    w('    <!-- Master Ground Plane -->')
    w('    <model name="ground_plane">')
    w('      <static>true</static>')
    w('      <link name="link">')
    w('        <collision name="collision"><geometry><plane><normal>0 0 1</normal><size>140 140</size></plane></geometry><surface><friction><ode><mu>100</mu><mu2>50</mu2></ode></friction></surface></collision>')
    w('        <visual name="visual"><geometry><plane><normal>0 0 1</normal><size>140 140</size></plane></geometry><material><ambient>0.5 0.6 0.4 1</ambient><diffuse>0.5 0.6 0.4 1</diffuse><pbr><metal><albedo_map>model://poultry_farm_world/materials/textures/grass_pasture.png</albedo_map></metal></pbr></material></visual>')
    w('      </link>')
    w('    </model>')
    w('')
    w('    <!-- Connecting Service Roadway -->')
    w('    <model name="inter_tunnel_service_road">')
    w('      <static>true</static><pose>0 8.0 0.015 0 0 0</pose>')
    w('      <link name="link">')
    w('        <collision name="collision"><geometry><box><size>30.0 6.0 0.03</size></box></geometry></collision>')
    w('        <visual name="visual"><geometry><box><size>30.0 6.0 0.03</size></box></geometry><material><ambient>0.75 0.75 0.75 1</ambient><diffuse>0.75 0.75 0.75 1</diffuse><pbr><metal><albedo_map>model://poultry_farm_world/materials/textures/concrete_floor.png</albedo_map></metal></pbr></material></visual>')
    w('      </link>')
    w('    </model>')
    w('')
    w('    <!-- Front Logistics Apron -->')
    w('    <model name="front_logistics_apron">')
    w('      <static>true</static><pose>-15.5 8.0 0.015 0 0 0</pose>')
    w('      <link name="link">')
    w('        <collision name="collision"><geometry><box><size>12.0 24.0 0.03</size></box></geometry></collision>')
    w('        <visual name="visual"><geometry><box><size>12.0 24.0 0.03</size></box></geometry><material><ambient>0.70 0.70 0.70 1</ambient><diffuse>0.70 0.70 0.70 1</diffuse><pbr><metal><albedo_map>model://poultry_farm_world/materials/textures/concrete_floor.png</albedo_map></metal></pbr></material></visual>')
    w('      </link>')
    w('    </model>')
    w('')
    w('    <!-- Outer Driveway Approach Road (Connecting Gate to Apron) -->')
    w('    <model name="driveway_approach_road">')
    w('      <static>true</static><pose>-24.0 8.0 0.012 0 0 0</pose>')
    w('      <link name="link">')
    w('        <collision name="collision"><geometry><box><size>8.0 6.0 0.024</size></box></geometry></collision>')
    w('        <visual name="visual"><geometry><box><size>8.0 6.0 0.024</size></box></geometry><material><ambient>0.65 0.65 0.65 1</ambient><diffuse>0.68 0.68 0.68 1</diffuse><pbr><metal><albedo_map>model://poultry_farm_world/materials/textures/concrete_floor.png</albedo_map></metal></pbr></material></visual>')
    w('      </link>')
    w('    </model>')
    w('')
    w('    <!-- ================================================================= -->')
    w('    <!-- PERIMETER FARM FENCING & FRONT ENTRANCE GATE                     -->')
    w('    <!-- ================================================================= -->')
    w('    <!-- Continuous boundary fencing enclosing X:[-21, +21], Y:[-15, +27] -->')
    w('    <include>')
    w('      <name>farm_perimeter_fence</name>')
    w('      <uri>model://farm_perimeter_fence</uri>')
    w('      <pose>0 0 0 0 0 0</pose>')
    w('    </include>')
    w('')
    w('    <!-- Grand Front Entrance Gate with Roman Named Signboard ("POULTRY FARM") -->')
    w('    <include>')
    w('      <name>farm_front_entrance_gate</name>')
    w('      <uri>model://farm_entrance_gate</uri>')
    w('      <pose>-21.0 8.0 0 0 0 0</pose>')
    w('    </include>')
    w('')
    w('    <!-- ================================================================= -->')
    w('    <!-- POULTRY FARM WORKERS (OUTER GARDEN, PADDOCK & LOGISTICS)        -->')
    w('    <!-- ================================================================= -->')
    w('    <!-- 1. Farm Supervisor: Standing on logistics apron near entrance gate -->')
    w('    <include>')
    w('      <name>worker_supervisor</name>')
    w('      <uri>model://farm_worker_supervisor</uri>')
    w('      <pose>-17.5 8.0 0 0 0 0</pose>')
    w('    </include>')
    w('')
    w('    <!-- 2. Caretaker 1: In the outer south garden / paddock watching free-range hens -->')
    w('    <include>')
    w('      <name>worker_caretaker_paddock</name>')
    w('      <uri>model://farm_worker_caretaker</uri>')
    w('      <pose>-2.5 -8.0 0 0 0 1.2</pose>')
    w('    </include>')
    w('')
    w('    <!-- 3. Caretaker 2: In outer grass garden near east paddock boundary -->')
    w('    <include>')
    w('      <name>worker_caretaker_garden</name>')
    w('      <uri>model://farm_worker_caretaker</uri>')
    w('      <pose>3.5 -7.0 0 0 0 -1.8</pose>')
    w('    </include>')
    w('')
    w('    <!-- 4. Logistics Operator 1: Near bulk feed storage silos -->')
    w('    <include>')
    w('      <name>worker_silo_operator</name>')
    w('      <uri>model://farm_worker_logistics</uri>')
    w('      <pose>-15.2 -2.5 0 0 0 1.57</pose>')
    w('    </include>')
    w('')
    w('    <!-- 5. Logistics Operator 2: Outside Egg Separation Mill loading dock -->')
    w('    <include>')
    w('      <name>worker_mill_operator</name>')
    w('      <uri>model://farm_worker_logistics</uri>')
    w('      <pose>-12.8 16.5 0 0 0 -0.5</pose>')
    w('    </include>')
    w('')
    w('    <!-- ================================================================= -->')
    w('    <!-- TUNNEL BARN 1: FLOOR HOUSING / BROILER & FREE-RANGE FLOCK         -->')
    w('    <!-- ================================================================= -->')
    w('    <include><name>poultry_barn_tunnel_1</name><uri>model://poultry_barn</uri><pose>0 0 0 0 0 0</pose></include>')
    w('    <model name="tunnel1_bedding_floor"><static>true</static><pose>0 0 0.01 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>23.6 9.6 0.02</size></box></geometry></collision><visual name="visual"><geometry><box><size>23.6 9.6 0.02</size></box></geometry><material><ambient>0.6 0.5 0.3 1</ambient><diffuse>0.7 0.6 0.4 1</diffuse><pbr><metal><albedo_map>model://poultry_farm_world/materials/textures/litter_bedding.png</albedo_map></metal></pbr></material></visual></link></model>')
    w('    <model name="tunnel1_central_runner"><static>true</static><pose>0 0 0.018 0 0 0</pose><link name="link"><visual name="visual"><geometry><box><size>23.4 1.5 0.005</size></box></geometry><material><ambient>0.7 0.7 0.7 1</ambient><diffuse>0.8 0.8 0.8 1</diffuse></material></visual></link></model>')
    w('    <model name="tunnel1_charging_dock"><static>true</static><pose>-11.2 0 0.025 0 0 0</pose><link name="link"><visual name="visual"><geometry><box><size>0.8 0.8 0.02</size></box></geometry><material><ambient>0.8 0.6 0.1 1</ambient><diffuse>0.9 0.7 0.1 1</diffuse></material></visual></link></model>')
    w('')
    w('    <!-- Tunnel 1 Feed Silos & Fans -->')
    w('    <include><name>feed_silo_1</name><uri>model://feed_silo</uri><pose>-14.5 -6.5 0 0 0 0</pose></include>')
    w('    <include><name>feed_silo_2</name><uri>model://feed_silo</uri><pose>-14.5 -3.5 0 0 0 0</pose></include>')
    w('    for fname, fx, fy, fz in [("t1_fan_1", 12.0, -2.4, 1.5), ("t1_fan_2", 12.0, -0.8, 1.5), ("t1_fan_3", 12.0, 0.8, 1.5), ("t1_fan_4", 12.0, 2.4, 1.5)]:')
    for fname, fx, fy, fz in [("t1_fan_1", 12.0, -2.4, 1.5), ("t1_fan_2", 12.0, -0.8, 1.5), ("t1_fan_3", 12.0, 0.8, 1.5), ("t1_fan_4", 12.0, 2.4, 1.5)]:
        w(f'    <include><name>{fname}</name><uri>model://tunnel_fan</uri><pose>{fx} {fy} {fz} 0 0 {math.pi}</pose></include>')
    w('')
    w('    <!-- Tunnel 1 Brooder Heaters -->')
    for hname, hx, hy in [("t1_heater_1", -6.0, 0.0), ("t1_heater_2", -2.0, 0.0), ("t1_heater_3", 2.0, 0.0), ("t1_heater_4", 6.0, 0.0)]:
        w(f'    <include><name>{hname}</name><uri>model://brooder_heater</uri><pose>{hx} {hy} 2.6 0 0 0</pose></include>')
    w('')
    w('    <!-- Tunnel 1 Feeder Lines & Drinker Lines -->')
    for idx, fx in enumerate([-9.0, -7.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0, 9.0]):
        w(f'    <include><name>t1_feeder_n_{idx+1}</name><uri>model://feeder_pan</uri><pose>{fx} 2.6 0.15 0 0 0</pose></include>')
        w(f'    <include><name>t1_feeder_s_{idx+1}</name><uri>model://feeder_pan</uri><pose>{fx} -2.6 0.15 0 0 0</pose></include>')
    for idx, dx in enumerate([-8.0, -4.0, 0.0, 4.0, 8.0]):
        w(f'    <include><name>t1_drinker_n_{idx+1}</name><uri>model://drinker_line</uri><pose>{dx} 1.4 0.28 0 0 0</pose></include>')
        w(f'    <include><name>t1_drinker_s_{idx+1}</name><uri>model://drinker_line</uri><pose>{dx} -1.4 0.28 0 0 0</pose></include>')
    w('')
    w('    <!-- Tunnel 1 Perches & Nesting Boxes -->')
    w('    <include><name>t1_perch_1</name><uri>model://perch_a_frame</uri><pose>-7.0 -3.6 0 0 0 0</pose></include>')
    w('    <include><name>t1_perch_2</name><uri>model://perch_a_frame</uri><pose>7.0 3.6 0 0 0 0</pose></include>')
    w('    <include><name>t1_nest_1</name><uri>model://nesting_box</uri><pose>-2.0 -4.4 0 0 0 0</pose></include>')
    w('    <include><name>t1_nest_2</name><uri>model://nesting_box</uri><pose>5.0 -4.4 0 0 0 0</pose></include>')
    w('')
    w('    <!-- Tunnel 1 Sensors & ArUco Markers -->')
    w('    <include><name>t1_sensor_1</name><uri>model://sensor_node</uri><pose>-5.0 4.85 1.6 0 0 -1.5708</pose></include>')
    w('    <include><name>t1_sensor_2</name><uri>model://sensor_node</uri><pose>5.0 4.85 1.6 0 0 -1.5708</pose></include>')
    w('    <include><name>t1_aruco_0</name><uri>model://aruco_marker_0</uri><pose>-11.8 -1.2 1.2 0 0 0</pose></include>')
    w('    <include><name>t1_aruco_1</name><uri>model://aruco_marker_1</uri><pose>-11.8 1.2 1.2 0 0 0</pose></include>')
    w('')
    w('    <!-- South Paddock Enclosure -->')
    w('    <model name="tunnel1_south_paddock"><static>true</static><link name="link">')
    w('      <visual name="f_s"><pose>0 -11.0 0.6 0 0 0</pose><geometry><box><size>14.0 0.05 1.2</size></box></geometry><material><ambient>0.6 0.45 0.3 1</ambient><diffuse>0.6 0.45 0.3 1</diffuse></material></visual>')
    w('      <collision name="c_s"><pose>0 -11.0 0.6 0 0 0</pose><geometry><box><size>14.0 0.1 1.2</size></box></geometry></collision>')
    w('      <visual name="f_w"><pose>-7.0 -8.0 0.6 0 0 0</pose><geometry><box><size>0.05 6.0 1.2</size></box></geometry><material><ambient>0.6 0.45 0.3 1</ambient><diffuse>0.6 0.45 0.3 1</diffuse></material></visual>')
    w('      <collision name="c_w"><pose>-7.0 -8.0 0.6 0 0 0</pose><geometry><box><size>0.1 6.0 1.2</size></box></geometry></collision>')
    w('      <visual name="f_e"><pose>7.0 -8.0 0.6 0 0 0</pose><geometry><box><size>0.05 6.0 1.2</size></box></geometry><material><ambient>0.6 0.45 0.3 1</ambient><diffuse>0.6 0.45 0.3 1</diffuse></material></visual>')
    w('      <collision name="c_e"><pose>7.0 -8.0 0.6 0 0 0</pose><geometry><box><size>0.1 6.0 1.2</size></box></geometry></collision>')
    w('    </link></model>')
    w('')
    w('    <!-- EGGS IN TUNNEL 1 (Nesting boxes & floor eggs) -->')
    egg_id = 1
    for dx_e, dy_e in [(-0.3, 0.0), (-0.1, 0.05), (0.1, -0.02), (0.3, 0.03)]:
        e_col = "brown" if egg_id % 2 == 0 else "white"
        w(f'    <include><name>t1_nest_egg_{egg_id}</name><uri>model://egg_{e_col}</uri><pose>{-2.0+dx_e:.2f} {-4.4+dy_e:.2f} 0.28 0 0 0</pose></include>')
        egg_id += 1
    for dx_e, dy_e in [(-0.25, 0.0), (0.0, 0.04), (0.25, -0.03)]:
        e_col = "brown" if egg_id % 2 == 0 else "white"
        w(f'    <include><name>t1_nest_egg_{egg_id}</name><uri>model://egg_{e_col}</uri><pose>{5.0+dx_e:.2f} {-4.4+dy_e:.2f} 0.28 0 0 0</pose></include>')
        egg_id += 1
    floor_egg_spots = [(-4.2, -3.5), (-1.8, 3.2), (0.5, -1.8), (3.6, -3.6), (6.2, 3.4), (-6.5, 3.7)]
    for fx_e, fy_e in floor_egg_spots:
        e_col = "brown" if egg_id % 2 == 0 else "white"
        w(f'    <include><name>t1_floor_egg_{egg_id}</name><uri>model://egg_{e_col}</uri><pose>{fx_e} {fy_e} 0.015 1.57 0 {random.uniform(0, 3.14):.2f}</pose></include>')
        egg_id += 1
    w('')
    w('    <!-- ================================================================= -->')
    w('    <!-- TUNNEL BARN 2: 5-LEVEL LAYER CAGE HOUSE & EGG SEPARATION MILL     -->')
    w('    <!-- ================================================================= -->')
    w('    <include><name>poultry_barn_tunnel_2</name><uri>model://poultry_barn</uri><pose>0 16.0 0 0 0 0</pose></include>')
    w('    <model name="tunnel2_concrete_floor"><static>true</static><pose>0 16.0 0.01 0 0 0</pose><link name="link"><collision name="collision"><geometry><box><size>23.6 9.6 0.02</size></box></geometry></collision><visual name="visual"><geometry><box><size>23.6 9.6 0.02</size></box></geometry><material><ambient>0.72 0.72 0.72 1</ambient><diffuse>0.75 0.75 0.75 1</diffuse><pbr><metal><albedo_map>model://poultry_farm_world/materials/textures/concrete_floor.png</albedo_map></metal></pbr></material></visual></link></model>')
    w('    <model name="tunnel2_inspection_aisle"><static>true</static><pose>0 16.0 0.018 0 0 0</pose><link name="link"><visual name="visual"><geometry><box><size>23.4 2.2 0.005</size></box></geometry><material><ambient>0.6 0.6 0.65 1</ambient><diffuse>0.65 0.65 0.70 1</diffuse></material></visual></link></model>')
    w('    <model name="tunnel2_docking_station"><static>true</static><pose>-11.2 16.0 0.025 0 0 0</pose><link name="link"><visual name="visual"><geometry><box><size>0.9 0.9 0.02</size></box></geometry><material><ambient>0.2 0.25 0.2 1</ambient><diffuse>0.25 0.85 0.45 1</diffuse></material></visual></link></model>')
    w('')
    w('    <!-- Tunnel 2 Feed Silos & Fans -->')
    w('    <include><name>feed_silo_3</name><uri>model://feed_silo</uri><pose>-14.5 22.5 0 0 0 0</pose></include>')
    w('    <include><name>feed_silo_4</name><uri>model://feed_silo</uri><pose>-14.5 25.8 0 0 0 0.3</pose></include>')
    for fname, fx, fy, fz in [("t2_fan_1", 12.0, 13.6, 1.5), ("t2_fan_2", 12.0, 15.2, 1.5), ("t2_fan_3", 12.0, 16.8, 1.5), ("t2_fan_4", 12.0, 18.4, 1.5)]:
        w(f'    <include><name>{fname}</name><uri>model://tunnel_fan</uri><pose>{fx} {fy} {fz} 0 0 {math.pi}</pose></include>')
    w('')
    w('    <!-- Tunnel 2 Sensors & ArUco Markers -->')
    w('    <include><name>t2_sensor_1</name><uri>model://sensor_node</uri><pose>-5.0 20.85 1.6 0 0 -1.5708</pose></include>')
    w('    <include><name>t2_sensor_2</name><uri>model://sensor_node</uri><pose>5.0 20.85 1.6 0 0 -1.5708</pose></include>')
    w('    <include><name>t2_aruco_2</name><uri>model://aruco_marker_2</uri><pose>-11.8 14.8 1.2 0 0 0</pose></include>')
    w('    <include><name>t2_aruco_3</name><uri>model://aruco_marker_3</uri><pose>-11.8 17.2 1.2 0 0 0</pose></include>')
    w('')
    w('    <!-- ================================================================= -->')
    w('    <!-- INDUSTRIAL EGG SEPARATION & GRADING MILL FACILITY                -->')
    w('    <!-- ================================================================= -->')
    w('    <include>')
    w('      <name>egg_separation_mill_station</name>')
    w('      <uri>model://egg_separation_mill</uri>')
    w('      <pose>-9.2 16.0 0 0 0 0</pose>')
    w('    </include>')
    w('')
    w('    <!-- 30-Egg Trays on Pallet & Packing Table -->')
    w('    <include><name>egg_tray_stack_1</name><uri>model://egg_tray_30</uri><pose>-6.8 14.8 0.55 0 0 0</pose></include>')
    w('    <include><name>egg_tray_stack_2</name><uri>model://egg_tray_30</uri><pose>-6.8 15.3 0.55 0 0 0</pose></include>')
    w('    <include><name>egg_tray_pallet_1</name><uri>model://egg_tray_30</uri><pose>-7.2 17.5 0.15 0 0 0.2</pose></include>')
    w('    <include><name>egg_tray_pallet_2</name><uri>model://egg_tray_30</uri><pose>-7.2 17.5 0.23 0 0 0.1</pose></include>')
    w('')
    w('    <!-- 5-TIER BATTERY CAGE RACKS (TWO LONG PARALLEL ROWS) -->')
    for uidx, rx in enumerate([-6.0, -2.0, 2.0, 6.0]):
        w(f'    <include><name>cage_rack_south_{uidx+1}</name><uri>model://cage_rack_5tier</uri><pose>{rx} 13.8 0 0 0 0</pose></include>')
        w(f'    <include><name>cage_rack_north_{uidx+1}</name><uri>model://cage_rack_5tier</uri><pose>{rx} 18.2 0 0 0 0</pose></include>')
    w('')
    w('    <!-- EGGS VISIBLE ALONG THE 5 TIERS OF CAGES (Front Roll-Out Trays) -->')
    tier_z_levels = [0.40, 0.90, 1.40, 1.90, 2.40]
    cage_egg_xs = [-5.5, -3.5, -1.5, 0.5, 2.5, 4.5, 6.5]
    for lvl_idx, z_h in enumerate(tier_z_levels):
        for ex in cage_egg_xs:
            e_col_s = "white" if (lvl_idx + int(ex)) % 2 == 0 else "brown"
            e_col_n = "brown" if (lvl_idx + int(ex)) % 2 == 0 else "white"
            w(f'    <include><name>rack_egg_s_L{lvl_idx+1}_{int(ex+10)}</name><uri>model://egg_{e_col_s}</uri><pose>{ex:.2f} 14.38 {z_h+0.02:.2f} 1.57 0 0</pose></include>')
            w(f'    <include><name>rack_egg_n_L{lvl_idx+1}_{int(ex+10)}</name><uri>model://egg_{e_col_n}</uri><pose>{ex:.2f} 17.62 {z_h+0.02:.2f} 1.57 0 0</pose></include>')
    w('')
    w('    <!-- HENS IN 5-TIER RACKS (TUNNEL 2) -->')
    cage_x_positions = [-7.2, -5.6, -4.0, -2.4, -0.8, 0.8, 2.4, 4.0, 5.6, 7.2]
    # South Rack Row (Y = 13.8)
    for lvl_idx, z_h in enumerate(tier_z_levels):
        for cidx, hx in enumerate(cage_x_positions):
            if (lvl_idx + cidx) % 2 == 0:
                breed = "brown" if (lvl_idx + cidx) % 3 == 0 else "white"
                pose = "pecking" if (cidx % 3 == 0) else "standing"
                w(f'    <include><name>hen_cage_s_f_L{lvl_idx+1}_{cidx+1}</name><uri>model://chicken_{breed}_{pose}</uri><pose>{hx:.2f} 14.15 {z_h:.2f} 0 0 1.571</pose></include>')
        for cidx in [0, 2, 4, 6, 8]:
            hx = cage_x_positions[cidx]
            breed = "white" if (lvl_idx + cidx) % 2 == 0 else "brown"
            w(f'    <include><name>hen_cage_s_b_L{lvl_idx+1}_{cidx+1}</name><uri>model://chicken_{breed}_standing</uri><pose>{hx:.2f} 13.45 {z_h:.2f} 0 0 -1.571</pose></include>')

    # North Rack Row (Y = 18.2)
    for lvl_idx, z_h in enumerate(tier_z_levels):
        for cidx, hx in enumerate(cage_x_positions):
            if (lvl_idx + cidx) % 2 == 1:
                breed = "brown" if (lvl_idx + cidx) % 2 == 1 else "white"
                pose = "pecking" if (cidx % 2 == 1) else "standing"
                w(f'    <include><name>hen_cage_n_f_L{lvl_idx+1}_{cidx+1}</name><uri>model://chicken_{breed}_{pose}</uri><pose>{hx:.2f} 17.85 {z_h:.2f} 0 0 -1.571</pose></include>')
        for cidx in [1, 3, 5, 7, 9]:
            hx = cage_x_positions[cidx]
            breed = "white" if (lvl_idx + cidx) % 3 == 0 else "brown"
            w(f'    <include><name>hen_cage_n_b_L{lvl_idx+1}_{cidx+1}</name><uri>model://chicken_{breed}_standing</uri><pose>{hx:.2f} 18.55 {z_h:.2f} 0 0 1.571</pose></include>')

    w('')
    w('    <!-- FLOOR HENS IN TUNNEL 1 (BROILER / CAGE-FREE FLOCK) -->')
    random.seed(42)
    flock_t1 = []
    # Chickens feeding at pans (facing directly towards pan centers at Y = ±2.6)
    # South pans (Y = -2.6):
    #   if Y = -2.35 (North of pan): face South (-Y) -> cyaw = -1.5708
    #   if Y = -2.85 (South of pan): face North (+Y) -> cyaw = +1.5708
    # North pans (Y = +2.6):
    #   if Y = +2.35 (South of pan): face North (+Y) -> cyaw = +1.5708
    #   if Y = +2.85 (North of pan): face South (-Y) -> cyaw = -1.5708
    for idx, (cx, cy, cyaw) in enumerate([
        (-9.0, -2.35, -1.5708), (-7.0, -2.85, 1.5708), (-5.0, -2.35, -1.5708), (-1.0, -2.85, 1.5708), (3.0, -2.35, -1.5708),
        (-9.0,  2.85, -1.5708), (-5.0,  2.35, 1.5708), (-1.0,  2.85, -1.5708), (3.0,  2.35, 1.5708), (7.0,  2.85, -1.5708)
    ]):
        breed = "white" if idx % 2 == 0 else "brown"
        flock_t1.append((f"t1_feed_{idx+1}", f"chicken_{breed}_pecking", cx, cy, 0.02, cyaw))

    for idx, (cx, cy, cyaw) in enumerate([
        (-8.2, -1.4, 0.0), (-4.2, -1.4, 3.14), (0.8, -1.4, 0.0), (4.8, -1.4, 3.14),
        (-6.2,  1.4, 0.0), (-2.2,  1.4, 3.14), (2.8,  1.4, 0.0), (6.8,  1.4, 3.14)
    ]):
        breed = "white" if idx % 2 == 1 else "brown"
        flock_t1.append((f"t1_drink_{idx+1}", f"chicken_{breed}_standing", cx, cy, 0.02, cyaw))

    # Well-separated roaming chickens (minimum 1.5m spacing to avoid any overlapping)
    roam_slots = [
        (-8.0, -3.7, 0.8), (-5.0, -3.4, -1.2), (-2.0, -3.7, 2.1), (1.5, -3.4, -0.5), (4.5, -3.7, 1.4), (7.5, -3.4, -2.3),
        (-7.5,  3.4, 1.1), (-4.5,  3.7, -1.8), (-1.5,  3.4, 0.4), (2.0,  3.7, -2.0), (5.0,  3.4, 1.7), (8.0,  3.7, -0.9)
    ]
    poses = ["pecking", "standing", "resting", "pecking", "standing", "pecking", "standing", "resting", "pecking", "standing", "resting", "pecking"]
    for idx, (rx, ry, ryaw) in enumerate(roam_slots):
        breed = "brown" if idx % 2 == 0 else "white"
        flock_t1.append((f"t1_roam_{idx+1}", f"chicken_{breed}_{poses[idx]}", rx, ry, 0.02, ryaw))

    for idx, (cx, cy, cyaw) in enumerate([(-4.0, -8.5, 0.5), (-1.5, -9.5, -1.0), (2.0, -8.0, 2.3), (4.5, -9.0, -2.1)]):
        flock_t1.append((f"t1_paddock_{idx+1}", "chicken_brown_pecking", cx, cy, 0.0, cyaw))

    for cname, cmodel, cx, cy, cz, cyaw in flock_t1:
        w(f'    <include><name>{cname}</name><uri>model://{cmodel}</uri><pose>{cx:.2f} {cy:.2f} {cz:.2f} 0 0 {cyaw:.3f}</pose></include>')

    w('')
    w('    <!-- ================================================================= -->')
    w('    <!-- NATURAL TREE SHELTERBELT OUTSIDE THE PERIMETER FENCE             -->')
    w('    <!-- All trees planted strictly OUTSIDE the fence (South, North, East, West) -->')
    w('    <!-- ================================================================= -->')

    random.seed(1234)
    tree_list = []

    # 1. South Shelterbelt (Y in [-27.0, -18.5], X from -32.0 to +32.0)
    for idx, tx in enumerate(np.linspace(-30.0, 30.0, 16)):
        ty = random.uniform(-25.0, -19.0)
        t_model = "pine_tree" if idx % 2 == 0 else "oak_tree"
        t_yaw = random.uniform(0, 6.28)
        tree_list.append((f"tree_south_{idx+1}", t_model, tx, ty, 0.0, t_yaw))

    # 2. North Shelterbelt (Y in [+30.5, +38.0], X from -32.0 to +32.0)
    for idx, tx in enumerate(np.linspace(-30.0, 30.0, 16)):
        ty = random.uniform(30.5, 36.5)
        t_model = "oak_tree" if idx % 2 == 0 else "pine_tree"
        t_yaw = random.uniform(0, 6.28)
        tree_list.append((f"tree_north_{idx+1}", t_model, tx, ty, 0.0, t_yaw))

    # 3. East Woodland (X in [+24.5, +33.0], Y from -22.0 to +32.0)
    for idx, ty in enumerate(np.linspace(-20.0, 30.0, 14)):
        tx = random.uniform(24.5, 32.0)
        t_model = "pine_tree" if idx % 2 == 1 else "oak_tree"
        t_yaw = random.uniform(0, 6.28)
        tree_list.append((f"tree_east_{idx+1}", t_model, tx, ty, 0.0, t_yaw))

    # 4. West Woodland (X in [-33.0, -25.0], Y from -22.0 to +32.0, leaving corridor at Y in [4, 12] for road)
    west_y_coords = [-22.0, -18.0, -14.0, -10.0, -6.0, -2.0, 1.0, 15.0, 19.0, 23.0, 27.0, 31.0]
    for idx, ty in enumerate(west_y_coords):
        tx = random.uniform(-32.0, -25.5)
        t_model = "oak_tree" if idx % 2 == 1 else "pine_tree"
        t_yaw = random.uniform(0, 6.28)
        tree_list.append((f"tree_west_{idx+1}", t_model, tx, ty, 0.0, t_yaw))

    for tname, tmodel, tx, ty, tz, tyaw in tree_list:
        w(f'    <include><name>{tname}</name><uri>model://{tmodel}</uri><pose>{tx:.2f} {ty:.2f} {tz:.2f} 0 0 {tyaw:.3f}</pose></include>')

    w('  </world>')
    w('</sdf>')

    output_path = os.path.join(WORLDS_DIR, "poultry_farm.sdf")
    with open(output_path, "w") as f:
        f.write("\n".join(sdf_lines))

    print(f"--> Saved {output_path} successfully!")
    print(f"    - Included {len(tree_list)} trees outside the perimeter fence.")
    print("    - Included perimeter fence & grand entrance gate with Roman named sign.")
    print("    - Included 5 poultry farm workers in outer garden & operations areas.")


if __name__ == "__main__":
    generate_world_sdf()
