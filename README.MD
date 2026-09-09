数据第0帧无对应相机位姿

# 点云输出

/bin/python3 /home/kcc/rgbd_nav/generate_pointcloud_gt1.py
/bin/python3 /home/kcc/rgbd_nav/generate_pointcloud_gt2.py
/bin/python3 /home/kcc/rgbd_nav/fuse.py
电脑内存不足，无法同时处理880帧数据，分为两次处理后再融合。
目前使用.gt文件的位姿。

# 查看点云ply文件

env DISPLAY=:0 XDG_SESSION_TYPE=x11 GLFW_PLATFORM=x11 python3 -c "import open3d as o3d; pcd = o3d.io.read_point_cloud('reconstructed_scene.ply'); o3d.visualization.draw_geometries([pcd])"

# 栅格地图

colcon build --packages-select pointcloud_to_occupancy

*发布点云话题*
python3 publish_pointcloud.py

*启动栅格地图生成以及rviz可视化*
ros2 launch pointcloud_to_occupancy occupancy_with_rviz.launch.py 

*保存栅格地图*
ros2 run nav2_map_server map_saver_cli -f ~/rgbd_nav/maps/my_occupancy_map --ros-args -r /map:=/occupancy_grid