import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # rviz is launched by robot_launch.py
    pkg_name = 'cart_nav_test'
    pkg_dir = get_package_share_directory(pkg_name)
    
    # Configuration file path
    configuration_directory = LaunchConfiguration(
        'configuration_directory',
        default=os.path.join(pkg_dir, 'config')
    )
    cartographer_config_lua = 'turtlebot3_lds_2d.lua'
    configuration_basename = LaunchConfiguration(
        'configuration_basename',
        default=cartographer_config_lua
    )

    resolution = LaunchConfiguration('resolution', default='0.05')
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='0.5')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    # Cartographer node
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        arguments=[
            '-configuration_directory', configuration_directory,
            '-configuration_basename', configuration_basename,
        ],
        remappings=[
            ('imu', '/imu'),
            ('odom', '/odometry/filtered'),
        ]
    )
    
    # Occupancy grid node - generates 2D map from 3D data
    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'resolution': resolution},
            {'publish_period_sec': publish_period_sec}
        ]
    )

    pointcloud_to_laserscan_config = os.path.join(
        get_package_share_directory('cart_nav_test'),
        'config',
        'pointcloud_to_laserscan.yaml'
    )

    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        remappings=[
            ('cloud_in', '/cropbox_filtered_cloud'),
            ('scan',     '/scan')
        ],
        parameters=[
                {'use_sim_time': True,
                'min_height': -1.15, #0.10, 
                'max_height': 0.1, #1.0,
                'range_max': 20.0,
                'target_frame': 'lidar_3d',
                },
            ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'configuration_directory',
            default_value=os.path.join(pkg_dir, 'config'),
            description='Directory containing Cartographer configuration files'
        ),
        DeclareLaunchArgument(
            'configuration_basename',
            default_value=cartographer_config_lua,
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
        pointcloud_to_laserscan_node,
        cartographer_node,
        occupancy_grid_node,
    ])