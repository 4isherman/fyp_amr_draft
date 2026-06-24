from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # voxel grid filter to remove excess points
    filter_voxel_grid_node = Node(
        package='pcl_ros',
        executable='filter_voxel_grid_node',
        name='filter_voxel_grid_node',
        remappings=[
            ('input', '/cropbox_filtered_cloud'),
            ('output', '/cloud_voxel')
        ],
        parameters=[{
            'use_sim_time': True,
            'filter_limit_max': 2.0,
            'filter_limit_min': -1.0,
            'leaf_size': 0.1  # 10cm resolution
        }]
    )

    # accumulate point cloud and save to pcd
    combined_pointcloud_to_pcd_node = Node(
        package='pcl_ros',
        executable='combined_pointcloud_to_pcd',
        name='combined_pointcloud_to_pcd',
        remappings=[
            ('input', '/cloud_voxel'), 
        ],
        parameters=[{
            'use_sim_time': True,
            'fixed_frame': 'map',
            'compressed' : True,
            'binary' : True,
        }],
    )

    return LaunchDescription([
        filter_voxel_grid_node,
        combined_pointcloud_to_pcd_node,
    ])




    # combined_pointcloud_to_pcd_node = Node(
    #     package='pcl_ros',
    #     executable='combined_pointcloud_to_pcd',
    #     name='combined_pointcloud_to_pcd',
    #     remappings=[
    #         ('input', '/cloud_final'), 
    #     ],
    #     parameters=[{
    #         'use_sim_time': True,
    #         'fixed_frame': 'map',
    #         # 'fixed_frame': 'base_footprint', # do not use, will smear
    #         'compressed' : True,
    #         'binary' : True,
    #         # 'rgb' : True,
    #     }],
    # )