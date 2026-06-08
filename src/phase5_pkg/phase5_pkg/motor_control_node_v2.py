import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
from rclpy.qos import QoSProfile,ReliabilityPolicy,HistoryPolicy,DurabilityPolicy

class MotorControlNode(Node):
    def __init__(self):
        super().__init__('motor_control_node')

        qos=QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE
        )

        self.sub=self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            qos
        )

        self.serial_port='/dev/ttyACM0'
        self.baudrate=115200

        try:
            self.ser=serial.Serial(
                self.serial_port,
                self.baudrate,
                timeout=1
            )

            self.get_logger().info('ESP32 serial connected')

        except Exception as e:
            self.get_logger().error(f'Serial connection failed: {e}')

        self.get_logger().info('Motor control node started')

    def cmd_callback(self, msg):

        linear = msg.linear.x
        angular = msg.angular.z

        # ---------------------------------
        # SEARCH MODE (rotate in place)
        # ---------------------------------
        if linear == 0.0 and abs(angular) > 0.05:

            turn_speed = int(angular * 180)

            left_speed = -turn_speed
            right_speed = turn_speed

        # ---------------------------------
        # FOLLOW MODE (move + steer)
        # ---------------------------------
        else:

            base_speed = 140

            turn_speed = int(angular * 220)

            left_speed = base_speed - turn_speed
            right_speed = base_speed + turn_speed
            right_speed = int(right_speed * 0.85)

        # Clamp
        left_speed = max(min(left_speed, 255), -255)
        right_speed = max(min(right_speed, 255), -255)

        # Deadzone filter
        if abs(left_speed) < 60:
            left_speed = 0

        if abs(right_speed) < 60:
            right_speed = 0

        command = f'{left_speed},{right_speed}\n'

        try:
            if hasattr(self, 'ser') and self.ser:
                self.ser.write(command.encode())

        except Exception as e:
            self.get_logger().error(
                f'Serial write failed: {e}'
            )

def main(args=None):
    rclpy.init(args=args)

    node=MotorControlNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if hasattr(node, 'ser') and node.ser:

            try:

                node.ser.write(b'0,0\n')
                node.ser.flush()

            except Exception as e:

                node.get_logger().error(
                    f'Failed to send stop command: {e}'
                )

        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__=='__main__':
    main()