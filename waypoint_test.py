import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped


def main():
    # 1. Start the ROS 2 system
    rclpy.init()
    navigator = BasicNavigator()

    # 2. Wait for navigation to completely activate
    print("Waiting for Navigation to start...")
    navigator.waitUntilNav2Active(localizer='robot_localization')

    # 3. Set the goal locations (Waypoints)
    goal_poses = []

    # --- WAYPOINT 1: ENTRANCE (Start Here) ---
    entrance = PoseStamped()
    entrance.header.frame_id = 'map'
    entrance.pose.position.x = 8.0
    entrance.pose.position.y = 0.0
    entrance.pose.orientation.w = 1.0
    goal_poses.append(entrance)

    # --- WAYPOINT 2: RACK 1 ---
    rack1 = PoseStamped()
    rack1.header.frame_id = 'map'
    rack1.pose.position.x = 12.0  
    rack1.pose.position.y = -0.0 
    rack1.pose.orientation.z = 0.0
    rack1.pose.orientation.w = 1.0
    goal_poses.append(rack1)

    # --- WAYPOINT 3: RACK 2 ---
    rack2 = PoseStamped()
    rack2.header.frame_id = 'map'
    rack2.pose.position.x = 15.5  
    rack2.pose.position.y = 6.5 
    rack2.pose.orientation.z = 0.5469588219941847 #0.0
    rack2.pose.orientation.w = 0.8371595111104776 #1.0
    goal_poses.append(rack2)

    # --- WAYPOINT 4: RACK 3 ---
    rack3 = PoseStamped()
    rack3.header.frame_id = 'map'
    rack3.pose.position.x = 19.0
    rack3.pose.position.y = 7.5 #8.5
    rack3.pose.orientation.z = 0.0
    rack3.pose.orientation.w = 1.0
    goal_poses.append(rack3)

    rack4 = PoseStamped()
    rack4.header.frame_id = 'map'
    rack4.pose.position.x = 22.0
    rack4.pose.position.y = 3.0
    rack4.pose.orientation.z = -0.732
    rack4.pose.orientation.w = 0.680
    goal_poses.append(rack4)

    # --- WAYPOINT 5: transition 1 ---
    transition1 = PoseStamped()
    transition1.header.frame_id = 'map'
    transition1.pose.position.x = 17.6  
    transition1.pose.position.y = 1.32
    transition1.pose.orientation.z = -1.0
    transition1.pose.orientation.w = 0.01743
    goal_poses.append(transition1)

    transition3 = PoseStamped()
    transition3.header.frame_id = 'map'
    transition3.pose.position.x = 11.0 
    transition3.pose.position.y = 0.0
    transition3.pose.orientation.z = -1.0
    transition3.pose.orientation.w = 0.005
    goal_poses.append(transition3)

    transition3 = PoseStamped()
    transition3.header.frame_id = 'map'
    transition3.pose.position.x = 6.0 
    transition3.pose.position.y = 0.0
    transition3.pose.orientation.z = -1.0
    transition3.pose.orientation.w = 0.005
    goal_poses.append(transition3)

    # --- WAYPOINT 5: transition 2 ---
    transition2 = PoseStamped()
    transition2.header.frame_id = 'map'
    transition2.pose.position.x = 0.0 
    transition2.pose.position.y = 0.0
    transition2.pose.orientation.z = -1.0
    transition2.pose.orientation.w = 0.005
    goal_poses.append(transition2)

    # --- WAYPOINT 6: Exit
    # exit_map = PoseStamped()
    # exit_map.header.frame_id = 'map'
    # exit_map.pose.position.x = 2.087
    # exit_map.pose.position.y = -1.66
    # # exit_map.pose.orientation.w = 1.0
    # goal_poses.append(exit_map)


    # 4. Send the robot on the patrol
    print("Starting Navigation...")
    navigator.followWaypoints(goal_poses)

    # 5. Keep the script running until finished
    while not navigator.isTaskComplete():
        # (Optional) You can print feedback here if you want
        pass

    # 6. Check result
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('Navigation Completed')
    else:
        print('Navigation Failed')
    rclpy.shutdown()

if __name__ == '__main__':
    main()

# class WaypointTesting(Node):
#     def __init__(self):
#         super().__init__("waypoint_testing")

#         self.waypoint_testing_ = self.create_publisher(PoseWithCovarianceStamped,
#                                                       'initialpose', 10)
        
#         self.get_logger().info("WaypointTesting started")

#     def cmd_vel_callback(self, msg: Twist):
#         # self.get_logger().info(f"\nLinear X: {msg.linear.x}, Y: {msg.linear.y}, Z:{msg.linear.z}\nAngular X: {msg.angular.x}, Y: {msg.angular.y}, Z:{msg.angular.z}\n")
#         linear_x = msg.linear.x
#         angular_z = msg.angular.z
#         serial_write_str = f"{linear_x:.3f},{angular_z:.3f}"
#         self.serial_port.write(serial_write_str.encode())
#         self.get_logger().info(f"Sent: {serial_write_str.strip()}")


# def main(args=None):
#     rclpy.init(args=args)
#     node = WaypointTesting()
#     rclpy.spin(node) # spin will make the node run indefinitely until killed

#     node.serial_port.close()
#     node.destroy_node()
#     rclpy.shutdown()