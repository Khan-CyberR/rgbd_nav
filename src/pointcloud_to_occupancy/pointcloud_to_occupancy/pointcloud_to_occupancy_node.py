#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
from nav_msgs.msg import OccupancyGrid
import numpy as np
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

class PointCloudToOccupancy(Node):
    def __init__(self):
        super().__init__('pointcloud_to_occupancy')

        self.declare_parameter('cloud_topic', '/nonground')
        self.declare_parameter('map_topic', '/occupancy_grid')
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('map_resolution', 0.02)
        self.declare_parameter('map_width', 60.0)
        self.declare_parameter('map_height', 60.0)
        self.declare_parameter('ground_height', 0.15)
        self.declare_parameter('obstacle_threshold', 0.15)
        self.declare_parameter('max_z', 2.0)

        self.cloud_topic = self.get_parameter('cloud_topic').value
        self.map_topic = self.get_parameter('map_topic').value
        self.map_frame = self.get_parameter('map_frame').value
        self.map_resolution = self.get_parameter('map_resolution').value
        self.map_width_m = self.get_parameter('map_width').value
        self.map_height_m = self.get_parameter('map_height').value
        self.ground_height = self.get_parameter('ground_height').value
        self.obstacle_threshold = self.get_parameter('obstacle_threshold').value
        self.max_z = self.get_parameter('max_z').value

        self.width_px = int(self.map_width_m / self.map_resolution)
        self.height_px = int(self.map_height_m / self.map_resolution)
        self.origin_x = -self.map_width_m / 2.0
        self.origin_y = -self.map_height_m / 2.0

        self.subscription = self.create_subscription(
            PointCloud2,
            self.cloud_topic,
            self.cloud_callback,
            10
        )
        self.get_logger().info(f'Subscribing to {self.cloud_topic}')

        qos_map = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )

        self.publisher = self.create_publisher(OccupancyGrid, self.map_topic, qos_map)
        self.get_logger().info(f'Publishing to {self.map_topic}')

        self.grid_data = np.full(self.width_px * self.height_px, -1, dtype=np.int8)
        self.timer = self.create_timer(0.1, self.publish_map)



    def cloud_callback(self, msg):
        try:
            points = []
            for p in pc2.read_points(msg, field_names=('x', 'y', 'z'), skip_nans=True):
                points.append((p[0], p[1], p[2]))
            if not points:
                self.get_logger().warn('Received empty point cloud')
                return
            points_np = np.array(points, dtype=np.float32)

            relative_z = points_np[:, 2] - self.ground_height
            mask = (relative_z > 0) & (relative_z < self.max_z)
            filtered = points_np[mask]

            if filtered.shape[0] == 0:
                self.get_logger().warn('No points above ground')
                self.grid_data.fill(-1)
                return

            x = filtered[:, 0]
            y = filtered[:, 1]
            u = ((x - self.origin_x) / self.map_resolution).astype(np.int32)
            v = ((y - self.origin_y) / self.map_resolution).astype(np.int32)
            valid = (u >= 0) & (u < self.width_px) & (v >= 0) & (v < self.height_px)
            u_valid = u[valid]
            v_valid = v[valid]
            indices = v_valid * self.width_px + u_valid

            self.grid_data.fill(0)
            self.grid_data[indices] = 100
            self.get_logger().debug(f'Processed {len(indices)} occupied cells')

        except Exception as e:
            self.get_logger().error(f'Error processing point cloud: {e}')


    def publish_map(self):
        grid_msg = OccupancyGrid()
        grid_msg.header.stamp = self.get_clock().now().to_msg()
        grid_msg.header.frame_id = self.map_frame

        grid_msg.info.resolution = self.map_resolution
        grid_msg.info.width = self.width_px
        grid_msg.info.height = self.height_px
        grid_msg.info.origin.position.x = self.origin_x
        grid_msg.info.origin.position.y = self.origin_y
        grid_msg.info.origin.position.z = 0.0
        grid_msg.info.origin.orientation.w = 1.0

        grid_msg.data = self.grid_data.tolist()
        self.publisher.publish(grid_msg)

def main(args=None):
    rclpy.init(args=args)
    node = PointCloudToOccupancy()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()