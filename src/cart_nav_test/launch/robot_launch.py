import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    # Get the package directory
    pkg_name = 'cart_nav_test'  # Replace with your package name
    pkg_dir = get_package_share_directory(pkg_name)
    
    # Path to URDF file
    urdf_file = os.path.join(pkg_dir, 'urdf', f'amr.urdf')  # Adjust path as needed
    # urdf_file = os.path.join(pkg_dir, 'urdf', 'amr.urdf.xacro')  # XACRO

    # Path to map file (optional)
    map_file = os.path.join(pkg_dir, 'maps', 'CARTOTEST_map.yaml')  # Adjust if you have a map

    # world_name = 'turtlebot3_world.world'
    world_name = 'parking_lot_plug.sdf'
    
    world_file_path = os.path.join(pkg_dir, 'worlds', f'{world_name}')
    
    # Read URDF content
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # use this for xacro
    # robot_desc = Command(['xacro ', urdf_file])
    
    # Declare launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file = LaunchConfiguration('world', default=world_file_path)
    
    # Robot State Publisher - publishes robot's state to tf
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': use_sim_time
        }]
    )
    
    # Joint State Publisher - publishes joint states for visualization
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Start robot localization using an Extended Kalman filter
    ekf_config = os.path.join(
        get_package_share_directory('cart_nav_test'),
        'config',
        'ekf_def.yaml'
        # 'ekf.yaml'
    )
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            ekf_config, 
            {'use_sim_time': use_sim_time}],
    )

    # EKF for gps
    navsat_node = Node(
        package="robot_localization",
        executable="navsat_transform_node",
        name="navsat_transform",
        output="screen",
        parameters=["config/navsat.yaml"],
        remappings=[
            ("imu/data", "/imu"),
            ("gps/fix", "/navsat"),
            ("odometry/filtered", "/odometry/filtered")
        ]
    )
    
    # Map Server (optional - if you have a map to display)
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_file,
            'use_sim_time': use_sim_time
        }]
    ) if os.path.exists(map_file) else None
    
    # Lifecycle manager for map server (needed to activate it)
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['map_server']
        }]
    ) if os.path.exists(map_file) else None
    
    # RViz2 with custom config
    rviz_config_file = os.path.join(pkg_dir, 'rviz', 'robot_view_nav.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else [],
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # Gazebo - Launch Gazebo Harmonic (gz sim)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 
                        'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': ['-r -v4 ', world_file],
        }.items()
    )
    
    # Spawn entity in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        # arguments=[
        #     '-name', 'my_robot',
        #     '-topic', '/robot_description',
        #     '-x', '-2',
        #     '-y', '0',
        #     '-z', '0.3',
        #     '-Y', '0.0',
        # ],
        arguments=[
            '-name', 'my_robot',
            '-topic', '/robot_description',
            '-x', '0',
            '-y', '0',
            '-z', '0.3',
            '-Y', '3.142',
        ],
        output='screen'
    )
    
    # Bridge between ROS2 and Gazebo - 3D LiDAR, Depth Camera, IMU, and GPS
    gz_ros_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Bridge the 3D lidar point cloud data
            '/lidar_3d/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            # Bridge depth camera RGB image
            '/camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            # Bridge depth camera depth image
            '/camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
            # Bridge depth camera point cloud
            '/camera/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            # Bridge camera info
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            # Bridge IMU data
            '/imu@sensor_msgs/msg/Imu@gz.msgs.IMU',
            # Bridge cmd_vel for robot control
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            # Bridge GPS/NavSat data
            '/navsat@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat',
            # Bridge Odometry data - CRITICAL FOR CARTOGRAPHER
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            # Bridge TF from Gazebo
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        output='screen'
    )

    # -------------- Lidar Filters -------------
    # passthrough filter to remove ground points
    filter_passthrough_node = Node(
        package='pcl_ros',
        executable='filter_passthrough_node',
        name='filter_passthrough_node',
        remappings=[
            ('input', '/lidar_3d/points'),
            ('output', '/passthrough_filtered_cloud')
        ],
        parameters=[{
            'use_sim_time': True,
            'filter_field_name': 'z',
            'filter_limit_min': -0.2,   # remove ground
            'filter_limit_max': 2.0,
            'filter_limit_negative': False
        }],
    )

    # crop box filter to remove points on robot
    filter_crop_box_node = Node(
        package='pcl_ros',
        executable='filter_crop_box_node',
        name='filter_crop_box_node',
        remappings=[
            ('input', '/passthrough_filtered_cloud'),
            ('output', '/cropbox_filtered_cloud')
        ],
        parameters=[{
            'input_frame': 'base_footprint',
            # 'input_frame': 'base_link',
            'min_x': -0.3,
            'max_x': 0.3,
            'min_y': -0.3,
            'max_y': 0.3,
            'min_z': 0.0,
            'max_z': 0.1,
            'negative': True   # THIS removes the box region
        }]
    )

    # voxel grid filter to remove excess points
    # output used for saving pcd only
    filter_voxel_grid_node = Node(
        package='pcl_ros',
        executable='filter_voxel_grid_node',
        name='filter_voxel_grid_node',
        remappings=[
            ('input', '/cropbox_filtered_cloud'),
            ('output', '/cloud_final')
        ],
        parameters=[{
            'filter_limit_max': 2.0,
            'filter_limit_min': -1.0,
            'leaf_size': 0.1  # 10cm resolution
        }]
    )

    launch_nodes = [
        DeclareLaunchArgument('use_sim_time', default_value='true',
                            description='Use simulation time'),
        DeclareLaunchArgument('world', default_value=world_file_path,
                            description='Path to world file'),
        DeclareLaunchArgument(
            'configuration_directory',
            default_value=os.path.join(pkg_dir, 'config'),
            description='Directory containing Cartographer configuration files'
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

        # map_server,
        # lifecycle_manager,

        robot_state_publisher,
        joint_state_publisher,
        rviz,
        gazebo,
        spawn_entity,
        gz_ros_bridge,
        ekf_node,
        navsat_node,
        filter_passthrough_node,
        filter_crop_box_node,
        filter_voxel_grid_node,
    ]
    
    # Add map server nodes if map exists
    # if map_server:
    #     launch_nodes.append(map_server)
    #     print(f"MAP SERVER EXISTS")
    # if lifecycle_manager:
    #     launch_nodes.append(lifecycle_manager)
    #     print(f"LIFECYCLE MANAGER EXISTS")
    
    return LaunchDescription(launch_nodes)