import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix


class GpsCovarianceFix(Node):
    def __init__(self):
        super().__init__('gps_covariance_fix')

        self.sub = self.create_subscription(
            NavSatFix,
            '/navsat',
            self.callback,
            10
        )

        self.pub = self.create_publisher(
            NavSatFix,
            '/navsat_corrected',
            10
        )

    def callback(self, msg):
        # gps covariance
        msg.position_covariance = [
            0.1, 0.0, 0.0,
            0.0, 0.1, 0.0,
            0.0, 0.0, 99999.0   # x, y position
        ]

        msg.position_covariance_type = 2
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = GpsCovarianceFix()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()