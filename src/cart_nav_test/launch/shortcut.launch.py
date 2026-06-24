import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Get the package directory
    pkg_name = 'cart_nav_test'  # Replace with your package name
    pkg_dir = get_package_share_directory(pkg_name)

    launch_dir = LaunchConfiguration(
        'launch_dir',
        default=os.path.join(get_package_share_directory(pkg_name), 'launch'))
    yolo_ros_pkg_dir = LaunchConfiguration(
        'yolo_ros_pkg_dir',
        default=os.path.join(get_package_share_directory('yolo_bringup'), 'launch'))
    
    robot_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_dir, '/robot.launch.py']),
            launch_arguments={}.items()
    )
    cartographer_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_dir, '/cartographer2d.launch.py']),
            launch_arguments={}.items()
    )
    nav2_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([launch_dir, '/nav2.launch.py']),
            launch_arguments={}.items()
    )
    yolo_ros_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([yolo_ros_pkg_dir, '/yolo.launch.py']),
        launch_arguments={
        'model': 'yolov8m.pt',
        # 'model': 'yolov8m-seg.pt',
        'input_image_topic': '/camera/image',
        'input_depth_topic': '/camera/depth_image',
        'input_depth_info_topic': '/camera/camera_info',
        'device': 'cuda',
        'use_3d': 'True',
        'threshold': '0.9',
        'use_sim_time': 'True',
        'depth_image_units_divisor': '1',
        'max_det': '5',
        # 'target_frame': 'camera_depth_frame',
        }.items()
    )

    # launch_nodes = [
    #     IncludeLaunchDescription(
    #         PythonLaunchDescriptionSource([launch_dir, '/robot_launch.py']),
    #         launch_arguments={}.items(),
    #     ),
    #     IncludeLaunchDescription(
    #         PythonLaunchDescriptionSource([launch_dir, '/cartographer2d.launch.py']),
    #         launch_arguments={}.items(),
    #     ),
    #     IncludeLaunchDescription(
    #         PythonLaunchDescriptionSource([launch_dir, '/nav2.launch.py']),
    #         launch_arguments={}.items(),
    #     ),
    # ]
    print(type(cartographer_launch))

    return LaunchDescription([
        robot_launch,
        # TimerAction(period=5.0, actions=[yolo_ros_launch, cartographer_launch]),
        TimerAction(period=5.0, actions=[cartographer_launch]),
        TimerAction(period=10.0, actions=[nav2_launch]),
        # TimerAction(period=15.0, actions=[yolo_ros_launch]),
    ])

    # return LaunchDescription(launch_nodes)