import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node


def generate_launch_description():
    pkg_description = get_package_share_directory('poultry_farm_description')
    xacro_file = os.path.join(pkg_description, 'urdf', 'poultry_bot.urdf.xacro')

    # Launch Configurations for Spawn Pose
    x_pose = LaunchConfiguration('x', default='-8.0')
    y_pose = LaunchConfiguration('y', default='0.0')
    z_pose = LaunchConfiguration('z', default='0.20')
    yaw_pose = LaunchConfiguration('yaw', default='0.0')

    # Process Xacro to Robot Description as string ParameterValue
    doc = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    # Robot State Publisher Node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': doc,
            'use_sim_time': True
        }]
    )

    # Gazebo Sim Entity Spawner Node
    node_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-name', 'poultry_bot',
            '-topic', 'robot_description',
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
            '-Y', yaw_pose
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument('x', default_value='-8.0', description='Initial spawn X coordinate'),
        DeclareLaunchArgument('y', default_value='0.0', description='Initial spawn Y coordinate'),
        DeclareLaunchArgument('z', default_value='0.20', description='Initial spawn Z coordinate'),
        DeclareLaunchArgument('yaw', default_value='0.0', description='Initial spawn Yaw angle'),
        node_robot_state_publisher,
        node_spawn_entity
    ])
