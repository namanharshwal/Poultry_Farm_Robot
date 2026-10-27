#!/usr/bin/env python3
"""
Dynamic Chicken Spawner for Poultry Farm Gazebo World.
Usage:
    python3 spawn_chicken.py --name my_chicken --breed white --pose standing --x 0.0 --y 0.0 --yaw 0.0
"""

import argparse
import subprocess
import sys


def spawn_chicken(name, breed, pose, x, y, z, yaw):
    model_name = f"chicken_{breed}_{pose}"
    sdf_string = f"""
    <sdf version='1.8'>
      <include>
        <name>{name}</name>
        <uri>model://{model_name}</uri>
        <pose>{x} {y} {z} 0 0 {yaw}</pose>
      </include>
    </sdf>
    """

    cmd = [
        "gz", "service",
        "-s", "/world/poultry_farm/create",
        "--reqtype", "gz.msgs.EntityFactory",
        "--reptype", "gz.msgs.Boolean",
        "--timeout", "3000",
        "--req", f'sdf: "{sdf_string.strip()}"'
    ]

    print(f"Spawning {name} ({model_name}) at ({x}, {y}, {z}, yaw={yaw})...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print("Successfully spawned chicken!")
        else:
            print(f"Spawn command output: {res.stderr or res.stdout}")
    except Exception as e:
        print(f"Error calling gz service: {e}")


def main():
    parser = argparse.ArgumentParser(description="Spawn a chicken into Gazebo Poultry Farm world.")
    parser.add_argument("--name", default="dynamic_chicken_1", help="Unique entity name")
    parser.add_argument("--breed", choices=["white", "brown"], default="white", help="Chicken breed")
    parser.add_argument("--pose", choices=["standing", "pecking", "resting"], default="standing", help="Chicken posture")
    parser.add_argument("--x", type=float, default=0.0, help="X position (meters)")
    parser.add_argument("--y", type=float, default=0.0, help="Y position (meters)")
    parser.add_argument("--z", type=float, default=0.02, help="Z position (meters)")
    parser.add_argument("--yaw", type=float, default=0.0, help="Yaw rotation (radians)")

    args = parser.parse_args()
    spawn_chicken(args.name, args.breed, args.pose, args.x, args.y, args.z, args.yaw)


if __name__ == "__main__":
    main()
