import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class ObstacleDetectionNode(Node):
    def __init__(self):
        super().__init__('obstacle_detection_node')

        self.obstacle_distance_threshold = 0.50
        self.front_angle_range = 20
        self.forward_speed = 0.20
        self.turn_speed = 0.50

        self.scan_subscriber = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.get_logger().info("Obstacle Detection Node Started")

    def scan_callback(self, msg: LaserScan):
        ranges = msg.ranges
        total_ranges = len(ranges)
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
            self.stop_robot()
            return

        min_front_distance = min(valid_front_ranges)

        self.get_logger().info(
            f"Front Distance: {min_front_distance:.2f} m"
        )

        if min_front_distance < self.obstacle_distance_threshold:

            self.get_logger().warn(
                f"Obstacle Detected at "
                f"{min_front_distance:.2f} m"
            )
            self.avoid_obstacle()

        else:
            self.move_forward()

    def move_forward(self):
        msg = Twist()
        msg.linear.x = self.forward_speed
        msg.angular.z = 0.0
        self.cmd_vel_publisher.publish(msg)

    def stop_robot(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.cmd_vel_publisher.publish(msg)

    def avoid_obstacle(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = self.turn_speed
        self.cmd_vel_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()