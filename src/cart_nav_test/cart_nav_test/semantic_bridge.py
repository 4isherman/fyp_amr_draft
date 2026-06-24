import rclpy
from rclpy.node import Node
from yolo_msgs.msg import DetectionArray
from geometry_msgs.msg import PointStamped

from semantic_costmap_layer_msgs.msg import SemanticObjectArray
from semantic_costmap_layer_msgs.msg import SemanticObject
import tf2_ros
import tf2_geometry_msgs

class SemanticBridge(Node):
    def __init__(self):
        super().__init__("semantic_bridge")

        self.sub = self.create_subscription(
            DetectionArray,
            "/yolo/detections_3d",
            self.callback,
            10
        )

        self.pub = self.create_publisher(
            SemanticObjectArray,
            "/semantic_objects",
            10
        )

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.get_logger().info("SemanticBridge started")

    def callback(self, msg):
        out = SemanticObjectArray()

        for det in msg.detections:
            obj = SemanticObject()

            obj.class_name = det.class_name
            obj.confidence = det.score
            obj.size = det.bbox3d.size
            # self.get_logger().info(f"Class Name: {obj.class_name}")
            # self.get_logger().info(f"Confidence: {obj.confidence}")

            p = PointStamped()
            # p.header = msg.header
            p.header.frame_id = "camera_depth_frame" #det.bbox3d.frame_id
            p.point = det.bbox3d.center.position
            # self.get_logger().info(f"before transform: {p.point}")

            # p.point = det.bbox.center.position
            # self.get_logger().info(f"Point: {p.point}")

            try:
                tf = self.tf_buffer.transform(
                    p,
                    "odom",
                    # "camera_depth_frame",
                    timeout=rclpy.duration.Duration(seconds=1.0)
                )
                tf.point.y += 0.6 # hardcoded offset as bounding box seems to be offset by that value
                obj.position = tf.point
                out.objects.append(obj)
                self.get_logger().info(f"Transformed obj: {obj}")
                # self.get_logger().info(f"{obj}")
                # self.get_logger().info(f"after transform: {obj.position}")
            except Exception as e:
                self.get_logger().warn(f"TF failed: {str(e)}")
                continue

        self.pub.publish(out)

def main(args=None):
    rclpy.init(args=args)
    node = SemanticBridge()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
