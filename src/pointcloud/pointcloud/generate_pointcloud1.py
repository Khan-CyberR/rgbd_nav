import open3d as o3d
import numpy as np
import os
from scipy.spatial.transform import Rotation as R

# --- 1. 设置路径 ---
# 假设你的数据在 'living_room_traj2_frei_png' 文件夹里
data_path = "/home/kcc/rgbd_nav/dataset/living_room_traj2_frei_png"
rgbd_path = data_path # rgb和depth子文件夹都在这里

# --- 2. 设置相机内参 (ICL-NUIM数据集固定参数) ---
# 针对640x480分辨率
width, height = 640, 480
fx, fy = 481.20, -480.00  # 注意：ICL-NUIM的fy是负值[reference:3]
cx, cy = 319.50, 239.50
intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, fx, fy, cx, cy)

# --- 3. 读取位姿 (Ground Truth Pose) ---
# 这里只是一个框架，具体解析取决于.gt.sim文件的格式
# 你需要编写代码读取文件中的每一帧位姿（通常是4x4变换矩阵）
def load_poses(pose_file_path):
    poses_dict = {}
    if not os.path.exists(pose_file_path):
        print(f"警告：位姿文件 {pose_file_path} 不存在")
        return []

    with open(pose_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = list(map(float, line.split()))
            if len(parts) != 8:
                print(f"跳过不符合格式的行: {line[:50]}...")
                continue
            idx = int(parts[0])          # 帧序号（从1开始）
            tx, ty, tz = parts[1], parts[2], parts[3]
            qx, qy, qz, qw = parts[4], parts[5], parts[6], parts[7]
            
            # 四元数转旋转矩阵 (scipy版本较新可支持)
            rot = R.from_quat([qx, qy, qz, qw]).as_matrix()
            trans = np.array([tx, ty, tz])
            
            # 构建4x4齐次矩阵
            mat = np.eye(4)
            mat[:3, :3] = rot
            mat[:3, 3] = trans
            poses_dict[idx] = mat
    
    # 按帧序号排序，返回列表（与图像列表顺序对应）
    sorted_idx = sorted(poses_dict.keys())
    poses = [poses_dict[i] for i in sorted_idx]
    return poses_dict

poses = load_poses(os.path.join(data_path, "livingRoom2.gt.freiburg"))

# --- 4. 遍历所有帧，生成并拼接点云 ---
# 假设你只使用前N帧，或者使用所有帧
# rgb和depth图片按时间戳命名，需要排序后一一对应
rgb_files = sorted(
    [f for f in os.listdir(os.path.join(rgbd_path, "rgb"))
     if f.endswith(".png")],
    key=lambda f: int(os.path.splitext(f)[0])
)

depth_files = sorted(
    [f for f in os.listdir(os.path.join(rgbd_path, "depth"))
     if f.endswith(".png")],
    key=lambda f: int(os.path.splitext(f)[0])
)

# 创建一个空点云来存放最终结果
final_pcd = o3d.geometry.PointCloud()

test_frame =600 #测试帧数

for i in range(test_frame, len(rgb_files)-1): # 或 range(0, len(rgb_files), 10) 来抽样
    # 读取彩色图和深度图
    color_raw = o3d.io.read_image(os.path.join(rgbd_path, 'rgb', rgb_files[i]))
    depth_raw = o3d.io.read_image(os.path.join(rgbd_path, 'depth', depth_files[i]))

    # 创建RGBD图像，深度缩放因子为1000.0（即深度图单位是毫米）[reference:4]
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_raw, depth_raw, depth_scale=5000.0, depth_trunc=30.0, convert_rgb_to_intensity=False)

    # 生成当前帧的点云
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsic)

    # 应用位姿变换，将点云转换到世界坐标系
    rgb_frame_id = int(os.path.splitext(rgb_files[i])[0])
    pose_id = rgb_frame_id + 1

    pose = poses.get(pose_id)
    if pose is None:
        print(f"RGB 帧 {rgb_frame_id} 没有对应的 pose {pose_id}，跳过")
        continue
    pcd.transform(pose)
    # if i < len(poses):
    #     pcd.transform(poses[i])
        #pcd.transform(np.linalg.inv(poses[i]))
    # 将当前帧点云拼接到最终点云
    final_pcd += pcd

# --- 5. 保存和可视化结果 ---
#体素降采样
final_pcd = final_pcd.voxel_down_sample(voxel_size=0.01)
o3d.io.write_point_cloud("reconstructed_scene2.ply", final_pcd)
o3d.visualization.draw_geometries([final_pcd])