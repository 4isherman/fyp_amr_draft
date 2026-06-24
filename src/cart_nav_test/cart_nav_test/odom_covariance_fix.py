import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from nav_msgs.msg import Odometry


class GpsCovarianceFix(Node):
    def __init__(self):
        super().__init__('gps_covariance_fix')

        self.sub = self.create_subscription(
            Odometry,
            '/odom_uncorrected',
            self.callback,
            10
        )

        self.pub = self.create_publisher(
            Odometry,
            '/odom',
            10
        )

    def callback(self, msg):

        # Example: ~0.5 m standard deviation
        # variance = 0.25

        msg.pose.covariance = [0.0] * 36

        # Position
        msg.pose.covariance[0] = 0.15 #0.05     # x variance
        msg.pose.covariance[7] = 0.15 #0.05     # y variance
        msg.pose.covariance[14] = 99999.0 # z unused

        # Orientation
        msg.pose.covariance[21] = 99999.0 # roll unused
        msg.pose.covariance[28] = 99999.0 # pitch unused
        msg.pose.covariance[35] = 0.05 #0.02    # yaw variance

        # msg.position_covariance_type = 2

        msg.twist.covariance = [0.0] * 36

        # Linear velocity
        msg.twist.covariance[0] = 0.05 #0.02      # vx
        msg.twist.covariance[7] = 99999.0   # vy (Ackermann usually constrained)
        msg.twist.covariance[14] = 99999.0  # vz unused

        # Angular velocity
        msg.twist.covariance[21] = 99999.0  # roll rate unused
        msg.twist.covariance[28] = 99999.0  # pitch rate unused
        msg.twist.covariance[35] = 0.05 #0.01     # yaw rate (ωz)

        self.pub.publish(msg)


def main():
    rclpy.init()
    node = GpsCovarianceFix()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()