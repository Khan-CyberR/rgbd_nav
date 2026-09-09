from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():

    config_file = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'config', 
        'point.rviz'
    )

    return LaunchDescription([
        # 通过命令行修改点云话题
        DeclareLaunchArgument(
            'topic',
            default_value='nonground',
            description='Point cloud topic to process'
        ),

        # 节点1：点云转占据栅格
        Node(
            package='pointcloud_to_occupancy',
            executable='pointcloud_to_occupancy',
            output='screen',
            parameters=[
                {'cloud_topic': LaunchConfiguration('topic')},
                {'map_topic': '/occupancy_grid'},
                {'map_frame': 'map'},
                {'map_resolution': 0.02},
                {'map_width': 10.0},
                {'map_height': 10.0},
                {'ground_height': 0.15},
                {'obstacle_threshold': 0.15},
                {'max_z': 2.0},
            ]
        ),

        # 节点2：静态 TF（提供 map 坐标系）
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
            output='screen'
        ),

        # 节点3：静态 TF（提供 base_link 坐标系）
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['-1.5', '1.5', '0', '0', '0', '0', 'odom', 'base_link'],
            output='screen'
        ),

        # 节点4：RViz（使用默认配置）
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', config_file]
        ),
    ])