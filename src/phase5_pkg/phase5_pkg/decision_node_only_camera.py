import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from vision_msgs.msg import Detection2DArray
from rclpy.qos import QoSProfile,ReliabilityPolicy,HistoryPolicy,DurabilityPolicy

class DecisionNode(Node):
    def __init__(self):
        super().__init__('decision_node')

        self.frame_width=640
        self.center_x=self.frame_width//2

        self.turn_threshold=60
        self.stop_width=320

        self.target_id=None
        self.search_direction=0.3

        qos=QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE
        )

        self.sub=self.create_subscription(
            Detection2DArray,
            '/tracked_detections',
            self.detection_callback,
            qos
        )

        self.pub=self.create_publisher(
            Twist,
            '/cmd_vel',
            qos
        )

        self.get_logger().info('Decision node started')

    def detection_callback(self,msg):
        twist=Twist()

        person_detections=[]

        for det in msg.detections:
            if len(det.results)==0:
                continue

            class_name=det.results[0].hypothesis.class_id

            if class_name=='person':
                person_detections.append(det)

        if len(person_detections)==0:
            twist.angular.z=self.search_direction
            self.pub.publish(twist)
            self.get_logger().info('Searching target')
            return

        target=None

        if self.target_id is not None:
            for det in person_detections:
                if det.id==self.target_id:
                    target=det
                    break

        if target is None:
            target=max(
                person_detections,
                key=lambda d:d.bbox.size_x*d.bbox.size_y
            )
            self.target_id=target.id

        cx=target.bbox.center.position.x
        width=target.bbox.size_x

        error=cx-self.center_x

        if width > 320:

            # FULL STOP
            twist.linear.x = 0.0
            twist.angular.z = 0.0

            self.get_logger().info(
                f'Target close stop | ID:{self.target_id}'
            )

        elif width > 250:

            # SLOW APPROACH
            twist.linear.x = 0.08
            twist.angular.z = -error * 0.002

        else:

            # NORMAL FOLLOW
            twist.linear.x = 0.15
            twist.angular.z = -error * 0.003


        # Ignore tiny steering jitter
        if abs(error) < 25:
            twist.angular.z = 0.0
            
            self.get_logger().info(
                f'Following target | error:{error}'
            )

        self.pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node=DecisionNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__=='__main__':
    main()