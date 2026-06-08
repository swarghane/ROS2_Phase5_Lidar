import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
from std_msgs.msg import Float32


class ObstacleDetectionNode(Node):
    def __init__(self):
        super().__init__('obstacle_detection_node')

        self.obstacle_distance_threshold = 0.50
        self.front_angle_range = 20

        self.scan_subscriber = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.obstacle_publisher = self.create_publisher(
            Bool,
            '/obstacle_detected',
            10
        )

        self.distance_publisher = self.create_publisher(
            Float32,
            '/front_distance',
            10
        )

        self.get_logger().info("Obstacle Detection Node Started")

    def scan_callback(self, msg: LaserScan):
        ranges = msg.ranges

        front_left = ranges[:self.front_angle_range]
        front_right = ranges[-self.front_angle_range:]

        front_ranges = list(front_left) + list(front_right)

        valid_front_ranges = [
            r for r in front_ranges
            if not math.isinf(r)
            and not math.isnan(r)
            and r > 0.0
        ]

        if len(valid_front_ranges) == 0:
            self.get_logger().warn("No valid LiDAR data")
            self.publish_obstacle_status(True, 0.0)
            return

        min_front_distance = min(valid_front_ranges)

        self.get_logger().info(
            f"Front Distance: {min_front_distance:.2f} m"
        )

        obstacle_detected = (
            min_front_distance <
            self.obstacle_distance_threshold
        )

        if obstacle_detected:
            self.get_logger().warn(
                f"Obstacle Detected at "
                f"{min_front_distance:.2f} m"
            )

        self.publish_obstacle_status(
            obstacle_detected,
            min_front_distance
        )

    def publish_obstacle_status(self, detected, distance):
        obstacle_msg = Bool()
        obstacle_msg.data = detected

        distance_msg = Float32()
        distance_msg.data = float(distance)

        self.obstacle_publisher.publish(obstacle_msg)
        self.distance_publisher.publish(distance_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()