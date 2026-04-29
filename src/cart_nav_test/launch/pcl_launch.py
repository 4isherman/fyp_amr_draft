import os
from launch import LaunchDescription
# from launch.actions import DeclareLaunchArgument

from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    """
    Launch Cartographer WITHOUT RViz.
    This allows it to connect to an already-running RViz instance.
    """
    pkg_name = 'cart_nav_test'
    pkg_dir = get_package_share_directory(pkg_name)
    
    # Configuration file path
    configuration_directory = LaunchConfiguration(
        'configuration_directory',
        default=os.path.join(pkg_dir, 'config')
    )
    
    configuration_basename = LaunchConfiguration(
        'configuration_basename',
        default=""
    )
    
    combined_pointcloud_to_pcd_node = Node(
        package='pcl_ros',
        executable='combined_pointcloud_to_pcd',
        name='combined_pointcloud_to_pcd',
        remappings=[
            ('input', '/lidar_3d/points'), 
        ],
        parameters=[
            # pointcloud_to_laserscan_config,
            {'use_sim_time': True,}],
    )

    filter_passthrough_node = Node(
        package='pcl_ros',
        executable='filter_passthrough_node',
        name='filter_passthrough_node',
        remappings=[
            ('input', '/lidar_3d/points'), 
        ],
        parameters=[
            # pointcloud_to_laserscan_config,
            {'use_sim_time': True,}],
    )

    # pointcloud_to_laserscan_node = Node(
    #     package='pointcloud_to_laserscan',
    #     executable='pointcloud_to_laserscan_node',
    #     name='pointcloud_to_laserscan',
    #     remappings=[
    #         ('cloud_in', '/lidar_3d/points'),   # your 3D lidar topic
    #         ('scan',     '/scan')               # output to Cartographer
    #     ],
    #     parameters=[
    #         # pointcloud_to_laserscan_config,
    #         {'use_sim_time': True,
    #          'min_height': 0.10, 
    #          'max_height': 1.0,
    #         'target_frame': 'base_footprint',
    #         }]
    # )

    
    return LaunchDescription([
        DeclareLaunchArgument(
            'configuration_directory',
            default_value=os.path.join(pkg_dir, 'config'),
            description='Directory containing Cartographer configuration files'
        ),
        DeclareLaunchArgument(
            'configuration_basename',
            default_value="",
            description='Basename of the Cartographer configuration file'
        ),
        DeclareLaunchArgument(
            'resolution',
            default_value='0.05',
            description='Resolution of the occupancy grid'
        ),
        DeclareLaunchArgument(
            'publish_period_sec',
            default_value='1.0',
            description='Period for publishing the occupancy grid'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'
        ),
        combined_pointcloud_to_pcd_node,
        # filter_passthrough_node,
    ])