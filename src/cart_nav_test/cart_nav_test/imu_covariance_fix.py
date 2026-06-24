import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu


class GpsCovarianceFix(Node):
    def __init__(self):
        super().__init__('gps_covariance_fix')

        self.sub = self.create_subscription(
            Imu,
            '/imu',
            self.callback,
            10
        )

        self.pub = self.create_publisher(
            Imu,
            '/imu_corrected',
            10
        )

    def callback(self, msg):
        # imu covariances
        msg.orientation_covariance = [
            99999.0, 0.0, 0.0,
            0.0, 99999.0, 0.0,
            0.0, 0.0, 0.01      # yaw position only
        ]

        msg.angular_velocity_covariance = [
            99999.0, 0.0, 0.0,
            0.0, 99999.0, 0.0,
            0.0, 0.0, 0.005     # yaw velocity only
        ]

        msg.linear_acceleration_covariance = [
            0.1, 0.0, 0.0,
            0.0, 99999.0, 0.0,
            0.0, 0.0, 99999.0   # x accel only
        ]
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = GpsCovarianceFix()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()