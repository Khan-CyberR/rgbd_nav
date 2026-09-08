import open3d as o3d
import numpy as np


# 读取两个点云
pcd1 = o3d.io.read_point_cloud("reconstructed_scene1.ply")
pcd2 = o3d.io.read_point_cloud("reconstructed_scene2.ply")

print(f"pcd1点数: {len(pcd1.points)}")
print(f"pcd2点数: {len(pcd2.points)}")

# 直接拼接
merged = pcd1 + pcd2

# 降采样
merged = merged.voxel_down_sample(voxel_size=0.02)

# 保存
o3d.io.write_point_cloud("merged.ply", merged)

