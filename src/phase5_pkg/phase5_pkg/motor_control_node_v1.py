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
        # STOPPING HANDLER (Target Close / No Target)
        # ---------------------------------
        # If both inputs are practically zero, stop immediately.
        if abs(linear) < 0.02 and abs(angular) < 0.02:
            left_speed = 0
            right_speed = 0

        # ---------------------------------
        # SEARCH MODE (rotate in place)
        # ---------------------------------
        elif abs(linear) < 0.02 and abs(angular) >= 0.02:
            # Scale up the search turn speed so it can clear the deadzone
            turn_speed = int(angular * 250) 
            
            left_speed = -turn_speed
            right_speed = turn_speed

        # ---------------------------------
        # FOLLOW MODE (move + steer dynamically)
        # ---------------------------------
        else:
            # Map base_speed directly to the incoming ROS linear velocity
            # Assuming incoming linear.x maxes out around 0.5 to 1.0 m/s
            base_speed = int(linear * 200) 
            
            # Dynamic steering modifier
            turn_speed = int(angular * 150)

            left_speed = base_speed - turn_speed
            right_speed = base_speed + turn_speed
            
            # Mechanical correction factor (Adjust 0.90 if it still drifts)
            # Apply to base speed or final speed depending on drift direction
            right_speed = int(right_speed * 0.90)

        # Final Clamp to PWM range
        left_speed = max(min(left_speed, 255), -255)
        right_speed = max(min(right_speed, 255), -255)

        # Lowered Deadzone filter (Allows low speed search rotations)
        # Change 35 based on when your specific motors physically start to nudge
        if abs(left_speed) < 35:
            left_speed = 0

        if abs(right_speed) < 35:
            right_speed = 0

        command = f'{left_speed},{right_speed}\n'

        try:
            if hasattr(self, 'ser') and self.ser:
                self.ser.write(command.encode())
        except Exception as e:
            self.get_logger().error(f'Serial write failed: {e}')

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