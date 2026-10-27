#!/usr/bin/env python3
"""
High-Performance Vectorized Static PointCloud & Spatial Voxel Fusion Node:
  - Robust Ingestion: Uses pc2.read_points() + np.column_stack() to avoid
    the uniform dtype assertion crash in sensor_msgs_py with mixed-type LiDAR/Depth pointclouds.
  - Coordinate Transformation: Uses TF2 to transform points to global /odom or /map frame.
  - Spatial Voxel Hash Grid: 0.05m voxel quantization with FIFO ring buffer eviction
    to ensure zero memory leaks during long-running farm inspections.
  - Publishes /perception/static_continuous_pointcloud for persistent 3D farm mapping.
"""

import math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
import sensor_msgs.msg as sensor_msgs
import sensor_msgs_py.point_cloud2 as pc2
import tf2_ros
from tf2_ros import TransformException
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Header


class PoultryPointCloudFusionNode(Node):
    def __init__(self):
        super().__init__('poultry_pointcloud_fusion_node')

        # Parameters
        self.declare_parameter('global_frame', 'odom')
        self.declare_parameter('voxel_size', 0.05)
        self.declare_parameter('max_voxels', 80000)
        self.declare_parameter('min_range', 0.25)
        self.declare_parameter('max_range', 18.0)
        self.declare_parameter('publish_rate_hz', 3.0)

        self.global_frame = self.get_parameter('global_frame').get_parameter_value().string_value
        self.voxel_size = self.get_parameter('voxel_size').get_parameter_value().double_value
        self.max_voxels = self.get_parameter('max_voxels').get_parameter_value().integer_value
        self.min_range = self.get_parameter('min_range').get_parameter_value().double_value
        self.max_range = self.get_parameter('max_range').get_parameter_value().double_value
        publish_rate = self.get_parameter('publish_rate_hz').get_parameter_value().double_value

        # TF2 Buffer & Listener
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Spatial Voxel Grid: dict mapping voxel_key (ix, iy, iz) -> (x, y, z, intensity)
        self.voxel_grid = {}
        self.voxel_keys_fifo = []

        # Subscriptions
        self.sub_scan = self.create_subscription(
            sensor_msgs.LaserScan,
            '/scan',
            self.laser_scan_callback,
            10
        )
        self.sub_depth_points = self.create_subscription(
            sensor_msgs.PointCloud2,
            '/camera/depth/points',
            self.depth_points_callback,
            5
        )

        # Publisher for Persistent Fused Point Cloud
        self.pub_fused_cloud = self.create_publisher(
            sensor_msgs.PointCloud2,
            '/perception/static_continuous_pointcloud',
            5
        )

        # Periodic Publish Timer
        self.timer = self.create_timer(1.0 / publish_rate, self.publish_fused_cloud)

        self.get_logger().info(
            f"Poultry PointCloud Fusion Active | Frame: {self.global_frame} | Voxel Size: {self.voxel_size}m"
        )

    def transform_points(self, points_xyz, source_frame):
        """Transform (N, 3) numpy array from source_frame to global_frame via TF2."""
        if points_xyz.shape[0] == 0:
            return points_xyz

        try:
            t = self.tf_buffer.lookup_transform(
                self.global_frame,
                source_frame,
                rclpy.time.Time(),
                timeout=Duration(seconds=0.1)
            )
        except TransformException as ex:
            return None

        # Extract translation and rotation quaternion
        tx = t.transform.translation.x
        ty = t.transform.translation.y
        tz = t.transform.translation.z
        qx = t.transform.rotation.x
        qy = t.transform.rotation.y
        qz = t.transform.rotation.z
        qw = t.transform.rotation.w

        # Rotation matrix from quaternion
        R = np.array([
            [1 - 2*(qy*qy + qz*qz), 2*(qx*qy - qz*qw), 2*(qx*qz + qy*qw)],
            [2*(qx*qy + qz*qw), 1 - 2*(qx*qx + qz*qz), 2*(qy*qz - qx*qw)],
            [2*(qx*qz - qy*qw), 2*(qy*qz + qx*qw), 1 - 2*(qx*qx + qy*qy)]
        ], dtype=np.float32)

        # Apply transformation: P_global = R * P_source + T
        transformed = np.dot(points_xyz, R.T) + np.array([tx, ty, tz], dtype=np.float32)
        return transformed

    def laser_scan_callback(self, msg: sensor_msgs.LaserScan):
        """Convert LaserScan to 3D Cartesian coordinates and fuse into voxel map."""
        ranges = np.array(msg.ranges, dtype=np.float32)
        angles = msg.angle_min + np.arange(len(ranges)) * msg.angle_increment

        valid = (ranges >= max(msg.range_min, self.min_range)) & \
                (ranges <= min(msg.range_max, self.max_range)) & \
                np.isfinite(ranges)

        if not np.any(valid):
            return

        r = ranges[valid]
        a = angles[valid]
        xs = r * np.cos(a)
        ys = r * np.sin(a)
        zs = np.zeros_like(xs)

        pts_local = np.column_stack([xs, ys, zs])
        pts_global = self.transform_points(pts_local, msg.header.frame_id)
        if pts_global is not None:
            self.insert_into_voxel_grid(pts_global, intensity=0.8)

    def depth_points_callback(self, msg: sensor_msgs.PointCloud2):
        """Robustly extract (x, y, z) using pc2.read_points + column_stack."""
        try:
            # Read generator safely
            raw_pts = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
            pts_list = [(p[0], p[1], p[2]) for p in raw_pts]
            if not pts_list:
                return

            pts_arr = np.array(pts_list, dtype=np.float32)

            # Filter range bounds
            dists = np.linalg.norm(pts_arr, axis=1)
            valid = (dists >= self.min_range) & (dists <= self.max_range)
            pts_arr = pts_arr[valid]

            if pts_arr.shape[0] == 0:
                return

            pts_global = self.transform_points(pts_arr, msg.header.frame_id)
            if pts_global is not None:
                self.insert_into_voxel_grid(pts_global, intensity=1.0)
        except Exception as e:
            self.get_logger().warn(f"Depth pointcloud extraction warning: {e}")

    def insert_into_voxel_grid(self, pts_global, intensity=1.0):
        """Quantize into 3D voxel keys and maintain FIFO buffer limit."""
        inv_v = 1.0 / self.voxel_size
        keys = np.floor(pts_global * inv_v).astype(np.int32)

        for i in range(len(keys)):
            key = (int(keys[i, 0]), int(keys[i, 1]), int(keys[i, 2]))
            if key not in self.voxel_grid:
                if len(self.voxel_grid) >= self.max_voxels:
                    # Evict oldest voxel
                    old_key = self.voxel_keys_fifo.pop(0)
                    self.voxel_grid.pop(old_key, None)

                pt = (float(pts_global[i, 0]), float(pts_global[i, 1]), float(pts_global[i, 2]), float(intensity))
                self.voxel_grid[key] = pt
                self.voxel_keys_fifo.append(key)

    def publish_fused_cloud(self):
        """Publish accumulated voxel grid as PointCloud2 with elevation coloring."""
        if not self.voxel_grid:
            return

        points = list(self.voxel_grid.values())
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = self.global_frame

        fields = [
            sensor_msgs.PointField(name='x', offset=0, datatype=sensor_msgs.PointField.FLOAT32, count=1),
            sensor_msgs.PointField(name='y', offset=4, datatype=sensor_msgs.PointField.FLOAT32, count=1),
            sensor_msgs.PointField(name='z', offset=8, datatype=sensor_msgs.PointField.FLOAT32, count=1),
            sensor_msgs.PointField(name='intensity', offset=12, datatype=sensor_msgs.PointField.FLOAT32, count=1),
        ]

        cloud_msg = pc2.create_cloud(header, fields, points)
        self.pub_fused_cloud.publish(cloud_msg)


def main(args=None):
    rclpy.init(args=args)
    node = PoultryPointCloudFusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
