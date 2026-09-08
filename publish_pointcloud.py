import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import open3d as o3d
import numpy as np
from sensor_msgs_py import point_cloud2 as pc2
from std_msgs.msg import Header

class PointCloudPublisher(Node):
    def __init__(self):
        super().__init__('pointcloud_publisher')
        self.publisher = self.create_publisher(PointCloud2, '/nonground', 10)
        # 读取你的PLY文件
        pcd = o3d.io.read_point_cloud("/home/kcc/rgbd_nav/merged.ply")
        points = np.asarray(pcd.points)
        # The dataset uses x-right, y-up, z-forward; ROS map uses x-forward,
        # y-left, z-up.
        self.points = np.column_stack((points[:, 2], -points[:, 0], points[:, 1]))
        self.get_logger().info(f'Loaded {len(self.points)} points.')

        # 创建一个定时器，每秒发布一次
        timer_period = 1.0
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = "map"  # 坐标系，确保和你的数据匹配
        cloud_msg = pc2.create_cloud_xyz32(header, self.points)
        self.publisher.publish(cloud_msg)
        self.get_logger().info('Publishing point cloud...')

def main(args=None):
    rclpy.init(args=args)
    node = PointCloudPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()