import os
import xacro
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_name = "my_car_description"
    pkg_share = FindPackageShare(package=pkg_name).find(pkg_name)
    
    urdf_xacro_path = os.path.join(pkg_share, "urdf", "my_car.urdf.xacro")
    rviz_config_path = os.path.join(pkg_share, "launch", "rviz_config.rviz")

    robot_desc = xacro.process_file(urdf_xacro_path).toxml()
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time, "robot_description": robot_desc}]
    )

    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}]
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="screen",
        arguments=["-d", rviz_config_path],
        parameters=[{"use_sim_time": use_sim_time}]
    )

    return LaunchDescription([
        joint_state_publisher_gui,
        robot_state_publisher,
        rviz_node
    ])