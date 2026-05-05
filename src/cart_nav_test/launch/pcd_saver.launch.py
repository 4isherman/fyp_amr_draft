import os
from launch import LaunchDescription
# from launch.actions import DeclareLaunchArgument

from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    combined_pointcloud_to_pcd_node = Node(
        package='pcl_ros',
        executable='combined_pointcloud_to_pcd',
        name='combined_pointcloud_to_pcd',
        remappings=[
            ('input', '/cloud_final'), 
        ],
        parameters=[{
            'use_sim_time': True,
            'fixed_frame': 'map',
            # 'fixed_frame': 'base_footprint', # do not use, will smear
            'compressed' : True,
            'binary' : True,
            # 'rgb' : True,
        }],
    )

    return LaunchDescription([
        combined_pointcloud_to_pcd_node,
    ])