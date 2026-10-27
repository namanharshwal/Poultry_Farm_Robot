#!/usr/bin/env bash
# ==============================================================================
# Poultry Farm Gazebo Simulation Launcher
# ==============================================================================

REAL_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "${REAL_PATH}")" && pwd)"
PACKAGE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

WORLD_FILE="${PACKAGE_DIR}/worlds/poultry_farm.sdf"
MODELS_DIR="${PACKAGE_DIR}/models"

echo "======================================================================"
echo "           STARTING POULTRY FARM GAZEBO SIMULATION                    "
echo "======================================================================"
echo "World File  : ${WORLD_FILE}"
echo "Models Path : ${MODELS_DIR}"
echo ""

# Export Gazebo / Ignition / SDFormat model search paths
export GZ_SIM_RESOURCE_PATH="${MODELS_DIR}:${PACKAGE_DIR}:${GZ_SIM_RESOURCE_PATH}"
export IGN_GAZEBO_RESOURCE_PATH="${MODELS_DIR}:${PACKAGE_DIR}:${IGN_GAZEBO_RESOURCE_PATH}"
export SDF_PATH="${MODELS_DIR}:${PACKAGE_DIR}:${SDF_PATH}"
export GAZEBO_MODEL_PATH="${MODELS_DIR}:${PACKAGE_DIR}:${GAZEBO_MODEL_PATH}"

# Detect simulator command
if command -v gz &>/dev/null && gz sim --help &>/dev/null; then
    SIM_CMD="gz sim"
elif command -v ign &>/dev/null && ign gazebo --help &>/dev/null; then
    SIM_CMD="ign gazebo"
else
    echo "[ERROR] Neither 'gz sim' nor 'ign gazebo' was found in PATH."
    exit 1
fi

echo "Simulator   : ${SIM_CMD}"
echo "Launching simulation now (press Ctrl+C to stop)..."
echo "======================================================================"

exec ${SIM_CMD} -r "${WORLD_FILE}" "$@"
