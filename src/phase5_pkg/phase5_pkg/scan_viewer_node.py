import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math


class ScanViewerNode(Node):

    def __init__(self):
        super().__init__('scan_viewer_node')

        self.subscription = self.create_subscription(
            LaserScan,'/scan',self.scan_callback,10)
        self.get_logger().info("Scan Viewer Node Started")

    def scan_callback(self, msg):
        ranges = msg.ranges
        valid_ranges = [
            r for r in ranges
            if not math.isinf(r) and not math.isnan(r)
        ]
        if len(valid_ranges) == 0:
            self.get_logger().warn("No valid scan data")
            return

        min_distance = min(valid_ranges)

        front_ranges = ranges[0:10] + ranges[-10:]

        valid_front = [
            r for r in front_ranges
            if not math.isinf(r) and not math.isnan(r)
        ]

        if len(valid_front) > 0:
            front_distance = min(valid_front)
        else:
            front_distance = float('inf')

        self.get_logger().info(
            f"Front: {front_distance:.2f} m | "
            f"Nearest: {min_distance:.2f} m"
        )


def main(args=None):
    rclpy.init(args=args)
    node = ScanViewerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()