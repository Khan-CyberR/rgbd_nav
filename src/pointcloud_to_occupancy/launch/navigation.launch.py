#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import subprocess
from launch.substitutions import Command

def generate_launch_description():

    map_yaml_file = "/home/kcc/rgbd_nav/maps/my_occupancy_map.yaml"
    params_file = "/home/kcc/rgbd_nav/src/pointcloud_to_occupancy/config/nav2_params.yaml"
    
    # ==================== 地图服务器（关键修复） ====================
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'yaml_filename': map_yaml_file
        }]
    )
    
    # ==================== 使用完整的Nav2启动配置 ====================
    nav2_components = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('nav2_bringup'),
            '/launch/navigation_launch.py'
        ]),
        launch_arguments={
            'use_sim_time': 'false',
            'params_file': params_file,
            'autostart': 'true',
            'use_composition': 'False',
            'container_name': '',
        }.items()
    )
    
    # ==================== 生命周期管理器（确保地图服务器和AMCL正确启动） ====================
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager',
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'autostart': True,
            'node_names': [
                'map_server',  # 确保地图服务器被管理
                # 'amcl',        # 确保AMCL被管理
                # 导航栈的其他节点由navigation_launch管理
            ]
        }]
    )
    
    # ==================== 使用说明 ====================
    usage_info = LogInfo(
        msg=f"""
        ================================
        地图文件: {map_yaml_file}
        ================================
        参数文件: {params_file}
        ================================
        """
    )
    
    # ==================== 创建启动描述 ====================
    ld = LaunchDescription()
    
    # 添加使用说明
    ld.add_action(usage_info)
    
    
    # 移除静态TF转换（由AMCL处理）
    # ld.add_action(static_transform_publisher)
    
    # 地图服务器（关键修复）
    ld.add_action(map_server_node)
    
    
    # 生命周期管理器
    ld.add_action(lifecycle_manager)

    
    # Nav2导航系统（延迟启动，等待Gazebo稳定）
    ld.add_action(TimerAction(
        period=5.0,
        actions=[nav2_components]
    ))
    
    return ld