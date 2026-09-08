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

*使用pointcloud_to_grid包，当前环境编译grid_map_cv失败，暂时跳过。*
source /opt/ros/humble/setup.bash
colcon build --packages-select grid_map_cmake_helpers grid_map_core grid_map_msgs --symlink-install
source install/setup.bash 

*open3d格式的ply文件无intensity信息，跳过显示*

ros2 launch pointcloud_to_grid demo.launch.py

ros2 launch pointcloud_to_grid rviz.launch.py 

python3 publish_pointcloud.py 