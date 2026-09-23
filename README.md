# ROS2 FYP Simulation
### Dependencies
- Ubuntu 24.04 LTS (Noble Numbat)
- ROS2 Jazzy
    - ```pcl_ros```
    - ```robot_localization```
    - ```cartographer_ros```
    - ```pointcloud_to_laserscan```
- Preferably Laptop/PC with CUDA support

### This repository also contains 2 other repositories:
- <a href="https://github.com/mgonzs13/yolo_ros"> yolo_ros</a> (González-Santamarta, M. Á. (2023))
- <a href="https://github.com/SeanReg/nav2_wavefront_frontier_exploration"> nav2_wavefront_frontier_exploration
</a> (Regan, S., & Sayed, O. (2020))


# Setup
1. Ensure correct Ubuntu and ROS2 version is already installed as stated above
2. Clone repository into desired folder
3. Manually add "source ```PATH_TO_REPO_FOLDER_NAME```/install/setup.bash" to .bashrc
    - alternatively, run ```echo "source PATH_TO_REPO_FOLDER_NAME/install/setup.bash" >> ~/.bashrc```
    - replace ```PATH_TO_REPO_FOLDER_NAME``` with full path to workspace folder
4. run ```colcon build``` in ```PATH_TO_REPO_FOLDER_NAME```

### Modifications
- semantic object detection behaviour can be modified in ```src\semantic_costmap_layer\src\semantic_layer.cpp```
- ```nav2_wfe``` can be modified at ```src\nav2_wfe\nav2_wfd\wavefront_frontier.py``` and
- ```yolo_ros``` can be modified at ```src\yolo_ros\yolo_bringup```, ```src\yolo_ros\yolo_msgs``` and ```src\yolo_ros\yolo_ros```
- sensor covariances can be modified at ```src\cart_nav_test\cart_nav_test\gps_covariance_fix.py```, ```src\cart_nav_test\cart_nav_test\imu_covariance_fix.py```, ```src\cart_nav_test\cart_nav_test\odom_covariance_fix.py```, 

# How to Run
### Full Simulation (Gazebo, RVIZ, Cartographer, nav2)
- In terminal, run ```ros2 launch cart_nav_test shortcut.launch.py```
    - ```shortcut.launch.py``` will call other launch files in ```cat_nav_test/launch``` folder
        - ```yolo_ros``` launch is called directly inside ```shortcut.launch.py```, launch params can be modified there
        - ```robot.launch.py``` will launch the Gazebo simulation, rviz2, and all the nodes with their respective configurations as defined in ```src\cart_nav_test\config```
            - simulation world file is located in ```src\cart_nav_test\worlds```
            - robot xacro is defined in ```src\cart_nav_test\urdf\amr_PROPER_acker.urdf.xacro```
- The launch folders include:
    - robot.launch.py
        - robot_state_publisher
        - joint_state_publisher
        - ekf_node
        - navsat_transform_node
        - rviz2
        - Gazebo Simualtion & Spawn Robot
        - parameter_bridge (ros_gz_bridge)
        - filter_passthrough_node (pcl_ros)
        - filter_crop_box_node (pcl_ros)
        - semantic_bridge_node
        - gps_covariance_fix_node
        - odom_covariance_fix_node
        - imu_covariance_fix_node
    - cartographer2d.launch.py
        - cartographer_node (cartographer_ros)
        - cartographer_occupancy_grid_node (cartographer_ros)
        - pointcloud_to_laserscan_node (pointcloud_to_laserscan)
    - nav2.launch.py
        - planner_server
        - controller_server
        - behavior_server
        - bt_navigator
        - collision_monitor
        - waypoint_follower
        - lifecycle_manager
    - pcd_saver.launch.py (will not be launched automatically)
        - combined_pointcloud_to_pcd (pcl_ros)
        - filter_voxel_grid_node (pcl_ros)

### Wavefront Frontier Exploration
- In terminal, run ```ros2 run nav2_wfd explore```
