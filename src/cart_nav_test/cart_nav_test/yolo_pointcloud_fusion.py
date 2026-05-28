import rclpy
from rclpy.node import Node

from yolo_msgs.msg import DetectionArray
from sensor_msgs.msg import PointCloud2, CameraInfo
from sensor_msgs_py import point_cloud2 as pc2

from semantic_costmap_layer_msgs.msg import SemanticObjectArray, SemanticObject
from geometry_msgs.msg import Point
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs
from geometry_msgs.msg import PointStamped
import numpy as np


class YoloPointCloudFusion(Node):

    def __init__(self):
        super().__init__('yolo_pointcloud_fusion')

        self.cloud = None
        self.camera_info = None

        self.sub_yolo = self.create_subscription(
            DetectionArray,
            '/yolo/detections',
            self.yolo_callback,
            10
        )

        self.sub_cloud = self.create_subscription(
            PointCloud2,
            '/camera/points',
            self.cloud_callback,
            10
        )

        self.sub_info = self.create_subscription(
            CameraInfo,
            '/camera/camera_info',
            self.info_callback,
            10
        )

        self.pub = self.create_publisher(
            SemanticObjectArray,
            '/semantic_objects',
            10
        )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def cloud_callback(self, msg):
        self.cloud = msg

    def info_callback(self, msg):
        self.camera_info = msg

    # def project_point(self, x, y, z, fx, fy, cx, cy):
    #     if z <= 0:
    #         return None
    #     u = fx * x / z + cx
    #     v = fy * y / z + cy
    #     return u, v
    def project_point(self, x, y, z, fx, fy, cx, cy):
        if z <= 0.05:
            return None

        u = fx * x / z + cx
        v = fy * y / z + cy

        if not np.isfinite(u) or not np.isfinite(v):
            return None

        return u, v

    def find_3d_from_bbox(self, u, v, cloud_msg, camera_info):
        fx = camera_info.k[0]
        fy = camera_info.k[4]
        cx = camera_info.k[2]
        cy = camera_info.k[5]

        best = None
        best_dist = 1e9

        # ROI sampling (fast enough for medium clouds)
        for x, y, z in pc2.read_points(
            cloud_msg,
            field_names=('x', 'y', 'z'),
            skip_nans=True
        ):
            ##
            if not np.isfinite(x) or not np.isfinite(y) or not np.isfinite(z):
                continue
            if z <= 0.05:
                continue
            ##!

            proj = self.project_point(x, y, z, fx, fy, cx, cy)
            if proj is None:
                continue

            du = proj[0] - u
            dv = proj[1] - v
            dist = du * du + dv * dv

            # keep only points close to bbox center
            if dist < best_dist:
                best_dist = dist
                best = (x, y, z)

        return best

    def yolo_callback(self, msg):

        if self.cloud is None or self.camera_info is None:
            return

        out = SemanticObjectArray()
        out.header = msg.header

        for det in msg.detections:

            # filter weak detections
            if det.score < 0.5:
                continue

            u = det.bbox.center.position.x
            v = det.bbox.center.position.y

            point = self.find_3d_from_bbox(
                u, v,
                self.cloud,
                self.camera_info
            )

            if point is None:
                continue

            obj = SemanticObject()

            obj.class_name = det.class_name
            obj.confidence = float(det.score)

            ##
            p = PointStamped()
            # p.header = msg.header
            # p.header.stamp = self.get_clock().now().to_msg()
            # p.header.frame_id = msg.header.frame_id
            # p.point.x = point[0]
            # p.point.y = point[1]
            # p.point.z = point[2]

            # p_odom = self.tf_buffer.transform(
            #     p,
            #     "odom",
            #     timeout=rclpy.duration.Duration(seconds=0.1)
            # )

            # obj.position = p_odom.point

            try:
                p.header.stamp = rclpy.time.Time().to_msg()
                p.header.frame_id = msg.header.frame_id

                p_odom = self.tf_buffer.transform(
                    p,
                    "odom",
                    timeout=rclpy.duration.Duration(seconds=0.05)
                )
                obj.position = p_odom.point

            except Exception as e:
                self.get_logger().warn(f"TF failed: {e}")
                return

            ##!

            # obj.position = Point(
            #     x=float(point[0]),
            #     y=float(point[1]),
            #     z=float(point[2])
            # )

            out.objects.append(obj)

        self.pub.publish(out)


def main():
    rclpy.init()
    node = YoloPointCloudFusion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()