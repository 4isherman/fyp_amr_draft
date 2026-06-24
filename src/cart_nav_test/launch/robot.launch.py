import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import xacro

def generate_launch_description():
    pkg_name = 'cart_nav_test'
    pkg_dir = get_package_share_directory(pkg_name)
    
    # world file name and path
    world_name = 'parking_lot_mod.sdf'
    # world_name = 'wavefront_map.sdf'
    world_file_path = os.path.join(pkg_dir, 'worlds', f'{world_name}')
    
    # load xacro
    robot_desc = Command([
        'xacro ',
        PathJoinSubstitution([
            FindPackageShare(pkg_name),
            'urdf',
            'amr_PROPER_acker.urdf.xacro'
        ])
    ])
    
    # launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_file = LaunchConfiguration('world', default=world_file_path)
    
    # publish robot state to tf
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
    
    # publish joint states for visualization in rviz
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # robot_localization package for Extended Kalman Filter
    ekf_config = os.path.join(
        get_package_share_directory('cart_nav_test'),
        'config',
        'ekf_def_mod.yaml'
    )
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            ekf_config,
            {'use_sim_time': use_sim_time},
        ],
    )

    # navsat_transform to transform gps data/coords into odometry data
    navsat_config = os.path.join(
        get_package_share_directory('cart_nav_test'),
        'config',
        'navsat.yaml'
    )
    navsat_node = Node(
        package="robot_localization",
        executable="navsat_transform_node",
        name="navsat_transform_node",
        output="screen",
        parameters=[
            navsat_config
         ],
        remappings=[
            # ("imu/data", "/imu"),
            ("imu/data", "/imu_corrected"),
            # ("gps/fix", "/navsat"),
            ("gps/fix", "/navsat_corrected"),
            # ("odometry/filtered", "/odometry/filtered")
            ("odometry/filtered", "/odom")
        ]
    )
    
    # load rviz
    rviz_config_file = os.path.join(pkg_dir, 'rviz', 'robot_view_nav.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else [],
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # launch gazebo
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
        arguments=[
            '-name', 'my_robot',
            '-topic', '/robot_description',
            '-x', '0',
            '-y', '0',
            '-z', '0.2',
            # '-Y', '3.142', # optional yaw setting
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

            # Bridge Odometry data
            '/odom_uncorrected@nav_msgs/msg/Odometry[gz.msgs.Odometry',

            # Bridge TF from Gazebo
            # '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        parameters=[
            {'use_sim_time': use_sim_time}
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
            'use_sim_time': use_sim_time,
            'filter_field_name': 'z',
            'filter_limit_min': -1.15, #-0.2,   # remove ground
            'filter_limit_max': 1.0, #2.0,
            'filter_limit_negative': False,}
        ],
    )

    # crop box filter to remove points on robot
    filter_crop_box_node = Node(
        package='pcl_ros',
        executable='filter_crop_box_node',
        name='filter_crop_box_node',
        remappings=[
            # ('input', '/passthrough_filtered_cloud'),
            ('input', '/lidar_3d/points'),
            ('output', '/cropbox_filtered_cloud'),
        ],
        parameters=[{
            'use_sim_time': use_sim_time,
            'input_frame': 'base_footprint',
            'min_x': -0.03,
            'max_x': 0.3,
            'min_y': -0.76 / 2,
            'max_y': 0.76 / 2,
            'min_z': 1.0,
            'max_z': 1.25,
            'negative': True,   # THIS removes the box region
        }],
    )

    # semantic node launch
    semantic_bridge_node = Node(
        package='cart_nav_test',
        executable='semantic_bridge',
        name='semantic_bridge'
    )

    # covariances for ekf
    gps_covariance_fix_node = Node(
        package='cart_nav_test',
        executable='gps_covariance_fix',
        name='gps_covariance_fix'
    )
    odom_covariance_fix_node = Node(
        package='cart_nav_test',
        executable='odom_covariance_fix',
        name='odom_covariance_fix'
    )
    imu_covariance_fix_node = Node(
        package='cart_nav_test',
        executable='imu_covariance_fix',
        name='imu_covariance_fix'
    )


    teleop_twist_joy_pkg_dir = LaunchConfiguration(
        'teleop_twist_joy_pkg_dir',
        default=os.path.join(get_package_share_directory('teleop_twist_joy'), 'launch'))
    
    teleop_config_file = os.path.join(pkg_dir, 'config', 'xbox.config.yaml')

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

        robot_state_publisher,
        joint_state_publisher,
        rviz,
        gazebo,
        spawn_entity,
        gz_ros_bridge,
        ekf_node,
        navsat_node,
        filter_crop_box_node,
        semantic_bridge_node,
        gps_covariance_fix_node,
        odom_covariance_fix_node,
        imu_covariance_fix_node,

        # teleop joystick launch
        # uncomment this if teleop with xbox controller
        # IncludeLaunchDescription(
        #     PythonLaunchDescriptionSource([teleop_twist_joy_pkg_dir, '/teleop-launch.py']),
        #     launch_arguments={
        #         'joy_config': '', # leave this empty so it will load only the config file
        #         'config_filepath': teleop_config_file
        #         }.items(),
        # ),
    ]

    
    return LaunchDescription(launch_nodes)