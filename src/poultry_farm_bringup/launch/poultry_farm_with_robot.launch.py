import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_env = get_package_share_directory('poultry_farm_environment')
    pkg_bringup = get_package_share_directory('poultry_farm_bringup')
    pkg_perception = get_package_share_directory('poultry_farm_perception')

    world_sdf = os.path.join(pkg_env, 'worlds', 'poultry_farm.sdf')
    models_dir = os.path.join(pkg_env, 'models')
    rviz_config = os.path.join(pkg_perception, 'rviz', 'poultry_farm_perception.rviz')

    use_rviz = LaunchConfiguration('rviz', default='false')

    # Environment variables for Gazebo model resolution
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=f"{models_dir}:{pkg_env}:{os.environ.get('GZ_SIM_RESOURCE_PATH', '')}"
    )

    # 1. Gazebo Sim Launch
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f"-r {world_sdf}"}.items()
    )

    # 2. Spawn AgriBot-AMR into Floor Barn 1
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bringup, 'launch', 'spawn_robot.launch.py')
        ),
        launch_arguments={
            'x': '-8.0',
            'y': '0.0',
            'z': '0.20',
            'yaw': '0.0'
        }.items()
    )

    # 3. ROS-GZ Parameter Bridge
    bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bringup, 'launch', 'bridge.launch.py')
        )
    )

    # 4. PointCloud & Spatial Voxel Fusion Node
    node_fusion = Node(
        package='poultry_farm_perception',
        executable='static_pointcloud_fusion_node.py',
        output='screen',
        parameters=[{
            'global_frame': 'odom',
            'voxel_size': 0.05,
            'max_voxels': 80000,
            'publish_rate_hz': 3.0
        }]
    )

    # 5. RViz2 (Conditional)
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        condition=launch.conditions.IfCondition(use_rviz)
    ) if 'launch' in globals() and hasattr(globals()['launch'], 'conditions') else Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config]
    )

    return LaunchDescription([
        set_gz_resource_path,
        DeclareLaunchArgument('rviz', default_value='false', description='Whether to launch RViz2'),
        gz_sim,
        spawn_robot,
        bridge,
        node_fusion,
    ])
