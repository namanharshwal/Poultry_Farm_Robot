import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    pkg_bringup = get_package_share_directory('poultry_farm_bringup')
    bridge_config = os.path.join(pkg_bringup, 'config', 'ros_gz_bridge.yaml')

    set_gz_partition = SetEnvironmentVariable('GZ_PARTITION', 'poultry_farm_robot')
    set_ign_partition = SetEnvironmentVariable('IGN_PARTITION', 'poultry_farm_robot')

    node_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=['--ros-args', '-p', f'config_file:={bridge_config}'],
        additional_env={
            'GZ_PARTITION': 'poultry_farm_robot',
            'IGN_PARTITION': 'poultry_farm_robot'
        }
    )

    return LaunchDescription([
        set_gz_partition,
        set_ign_partition,
        node_bridge
    ])
