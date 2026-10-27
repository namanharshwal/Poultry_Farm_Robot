#!/bin/bash
# ==============================================================================
# 🐔 AgriBot-AMR: Poultry Farm Gazebo Simulation & Autonomous Stack Launcher
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$SCRIPT_DIR"
WORLD_PATH="$WORKSPACE_DIR/src/poultry_farm_environment/worlds/poultry_farm.sdf"
MODELS_PATH="$WORKSPACE_DIR/src/poultry_farm_environment/models"

# 1. Clean Stale Simulation Processes
pkill -9 -f "gz sim" 2>/dev/null || true
pkill -9 -f "gz-sim-server" 2>/dev/null || true
pkill -9 -f "gz-gui" 2>/dev/null || true
pkill -9 -f "parameter_bridge" 2>/dev/null || true
pkill -9 -f "robot_state_publisher" 2>/dev/null || true
pkill -9 -f "rviz2" 2>/dev/null || true
pkill -9 -f "poultry_farm_gcs" 2>/dev/null || true
pkill -9 -f "poultry_inspection_controller" 2>/dev/null || true
pkill -9 -f "static_pointcloud_fusion_node" 2>/dev/null || true

# 2. Export Transport Partition & Resource Paths
export GZ_PARTITION=poultry_farm_robot
export IGN_PARTITION=poultry_farm_robot
export GZ_IP=127.0.0.1
export IGN_IP=127.0.0.1
export ROS_DOMAIN_ID=55

export GZ_SIM_RESOURCE_PATH="$MODELS_PATH:$WORKSPACE_DIR/src:$WORKSPACE_DIR/src/poultry_farm_environment:$GZ_SIM_RESOURCE_PATH"
export IGN_GAZEBO_RESOURCE_PATH="$MODELS_PATH:$WORKSPACE_DIR/src:$WORKSPACE_DIR/src/poultry_farm_environment:$IGN_GAZEBO_RESOURCE_PATH"
export SDF_PATH="$MODELS_PATH:$WORKSPACE_DIR/src:$WORKSPACE_DIR/src/poultry_farm_environment:$SDF_PATH"
export GAZEBO_MODEL_PATH="$MODELS_PATH:$WORKSPACE_DIR/src:$GAZEBO_MODEL_PATH"

export DISPLAY="${DISPLAY:-:1}"
export XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}"

echo "=================================================================="
echo "🐔 LAUNCHING AGRIBOT-AMR POULTRY FARM SIMULATION"
echo "=================================================================="
echo "📍 World:     $WORLD_PATH"
echo "📦 Models:    $MODELS_PATH"
echo "🖥️  Display:   $DISPLAY"
echo "🔒 Partition: $GZ_PARTITION"
echo "=================================================================="

# Source ROS 2
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

if [ -f "$WORKSPACE_DIR/install/setup.bash" ]; then
    source "$WORKSPACE_DIR/install/setup.bash"
fi

MODE="${1:-world}"

if [ "$MODE" == "headless" ]; then
    echo "Starting Gazebo in HEADLESS mode..."
    gz sim -s -r --headless-rendering "$WORLD_PATH"
elif [ "$MODE" == "world" ] || [ "$MODE" == "gui" ]; then
    echo "Launching Standalone Poultry Farm World in Gazebo Sim GUI..."
    gz sim -r "$WORLD_PATH"
elif [ "$MODE" == "robot" ] || [ "$MODE" == "amr" ]; then
    echo "Launching Complete Farm Environment with AgriBot-AMR & Sensor Fusion..."
    ros2 launch poultry_farm_bringup poultry_farm_with_robot.launch.py
elif [ "$MODE" == "gcs" ] || [ "$MODE" == "remote" ]; then
    echo "Starting AgriBot-AMR Operator Ground Control Station (GCS HUD)..."
    python3 "$WORKSPACE_DIR/src/poultry_farm_gcs/scripts/poultry_farm_gcs.py"
elif [ "$MODE" == "teleop" ]; then
    echo "Starting Terminal Teleoperation Console with Speed Governor..."
    python3 "$WORKSPACE_DIR/src/poultry_farm_control/scripts/amr_teleop_keyboard.py"
elif [ "$MODE" == "patrol" ] || [ "$MODE" == "autonomy" ]; then
    echo "Starting Autonomous Barn Aisle Inspection & Telemetry Controller..."
    python3 "$WORKSPACE_DIR/src/poultry_farm_control/scripts/poultry_inspection_controller.py"
elif [ "$MODE" == "rviz" ]; then
    echo "Launching RViz2 with Poultry Farm Perception Layout..."
    rviz2 -d "$WORKSPACE_DIR/src/poultry_farm_perception/rviz/poultry_farm_perception.rviz"
elif [ "$MODE" == "full" ]; then
    echo "Launching COMPLETE SYSTEM STACK (World + Robot + Fusion + GCS)..."
    ros2 launch poultry_farm_bringup poultry_farm_with_robot.launch.py &
    sleep 4
    python3 "$WORKSPACE_DIR/src/poultry_farm_gcs/scripts/poultry_farm_gcs.py"
else
    echo "Usage: ./launch_world.sh [world|robot|gcs|teleop|patrol|rviz|full|headless]"
    exit 1
fi
