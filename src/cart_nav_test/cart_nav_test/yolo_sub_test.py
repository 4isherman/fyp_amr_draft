#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
# from yolo_msgs.msg._detection_array import DetectionArray
from yolo_msgs.msg import DetectionArray
from serial import Serial

class CmdVelSubscriberNode(Node):
    def __init__(self):
        super().__init__("cmd_vel_subscriber")

        # self.serial_port = Serial('/dev/ttyACM0', 9600, timeout=1)

        self.cmd_vel_subscriber_ = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_vel_callback, 10)
        
        self.detection_array_subscriber_ = self.create_subscription(
            DetectionArray, "/yolo/detections", self.detection_array_callback, 10)
        
        self.get_logger().info("CmdVelSubscriberNode started")

    def cmd_vel_callback(self, msg: Twist):
        # self.get_logger().info(f"\nLinear X: {msg.linear.x}, Y: {msg.linear.y}, Z:{msg.linear.z}\nAngular X: {msg.angular.x}, Y: {msg.angular.y}, Z:{msg.angular.z}\n")
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        serial_write_str = f"{linear_x:.3f},{angular_z:.3f}"
        # self.serial_port.write(serial_write_str.encode())
        self.get_logger().info(f"Sent: {serial_write_str.strip()}")

    def detection_array_callback(self, msg: DetectionArray):
        # self.get_logger().info(f"\nLinear X: {msg.linear.x}, Y: {msg.linear.y}, Z:{msg.linear.z}\nAngular X: {msg.angular.x}, Y: {msg.angular.y}, Z:{msg.angular.z}\n")
        # if len(msg.detections) is not 0:
        if len(msg.detections) != 0:
            self.get_logger().info(f"{msg.detections[0].class_name}")

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelSubscriberNode()
    rclpy.spin(node) # spin will make the node run indefinitely until killed

    # node.serial_port.close()
    node.destroy_node()
    rclpy.shutdown()

