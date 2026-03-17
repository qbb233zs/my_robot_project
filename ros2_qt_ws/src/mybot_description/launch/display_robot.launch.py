import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # 1. 获取fishbot_description功能包的路径
    pkg_share = FindPackageShare(package='mybot_description')

    # 2. 精准指向你的fishbot.urdf.xacro文件（完全匹配你的目录结构）
    default_model_path = PathJoinSubstitution([pkg_share, 'urdf', 'mybot', 'mybot.urdf.xacro'])
    # rviz配置文件路径（如果你还没生成，启动时可以先注释掉arguments这行）
    default_rviz_config_path = PathJoinSubstitution([pkg_share, 'config', 'display_robot_model.rviz'])

    # 声明模型路径参数
    model_arg = DeclareLaunchArgument(
        name='model',
        default_value=default_model_path,
        description='机器人模型文件的绝对路径'
    )

    # 解析xacro模型，自动处理嵌套的include文件
    robot_description_content = ParameterValue(
        Command(['xacro ', LaunchConfiguration('model')]),
        value_type=str
    )

    # 发布机器人模型和TF坐标
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}],
        output='screen'
    )

    # 启动关节控制GUI，方便调试轮子、关节
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    # 启动rviz2可视化
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        # 如果你还没有rviz配置文件，先把下面这行注释掉
        arguments=['-d', default_rviz_config_path],
        output='screen'
    )

    return LaunchDescription([
        model_arg,
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        rviz_node
    ])