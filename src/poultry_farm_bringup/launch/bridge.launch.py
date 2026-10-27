import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_bringup = get_package_share_directory('poultry_farm_bringup')
    bridge_config = os.path.join(pkg_bringup, 'config', 'ros_gz_bridge.yaml')

    node_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=['--ros-args', '-p', f'config_file:={bridge_config}']
    )

    return LaunchDescription([
        node_bridge
    ])
