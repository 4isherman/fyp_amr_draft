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
    
    # cartographer_config_lua = 'amr_cart_minimal.lua'
    # cartographer_config_lua = 'amr_cart_new.lua'
    cartographer_config_lua = 'turtlebot3_lds_2d.lua'
    # cartographer_config_lua = '2d_test.lua'
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
        parameters=[{'use_sim_time': True}],
        arguments=[
            '-configuration_directory', configuration_directory,
            '-configuration_basename', configuration_basename,
        ],
        # remappings=[
        #     ('points2', '/lidar_3d/points'),
        #     # ('points2', '/scan'),
        #     ('imu', '/imu'),
        #     ('odom', '/odom'),
        # ]        
        remappings=[
            # ('points2', '/lidar_3d/points'),
            # ('points2', '/scan'),
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
            {'use_sim_time': True},
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
            # ('cloud_in', '/lidar_3d/points'),   # your 3D lidar topic
            ('cloud_in', '/cropbox_filtered_cloud'),
            ('scan',     '/scan')               # output to Cartographer
        ],
        parameters=[
            # pointcloud_to_laserscan_config,
            {'use_sim_time': True,
             'min_height': 0.10, 
             'max_height': 1.0,
            'target_frame': 'base_footprint',
            }]
    )

    # ---- Nav2 ----
    # nav2_bringup = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([
    #         os.path.join(get_package_share_directory('nav2_bringup'),
    #                      'launch', 'navigation_launch.py')
    #     ]),
    #     launch_arguments={
    #         'use_sim_time': 'true',
    #         'params_file': os.path.join(pkg_dir, 'config', 'nav2_params.yaml'),
    #     }.items()
    # )

    nav2_params = os.path.join(pkg_dir, 'config', 'nav2_params_tuned_2d.yaml')
    # nav2_params = os.path.join(pkg_dir, 'config', 'nav2_params_burger.yaml')

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_params]
    )

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_params],
        remappings=[('cmd_vel', 'cmd_vel_nav')]
    )

    smoother_server = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        parameters=[nav2_params]
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[nav2_params]
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[nav2_params]
    )

    velocity_smoother = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=[nav2_params],
        remappings=[
            ('cmd_vel', 'cmd_vel_nav'),
            ('cmd_vel_smoothed', 'cmd_vel')
        ]
    )

    collision_monitor = Node(
        package='nav2_collision_monitor',
        executable='collision_monitor',
        name='collision_monitor',
        output='screen',
        parameters=[nav2_params]
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'planner_server',
                'controller_server',
                'smoother_server',
                'bt_navigator',
                'behavior_server',
                'velocity_smoother',
                'collision_monitor',
            ]
        }]
    )
    # ---- !Nav2 ----
    
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
        # nav2_bringup,
        # planner_server,
        # controller_server,
        # smoother_server,
        # behavior_server,
        # bt_navigator,
        # velocity_smoother,
        # collision_monitor,
        # lifecycle_manager,
    ])