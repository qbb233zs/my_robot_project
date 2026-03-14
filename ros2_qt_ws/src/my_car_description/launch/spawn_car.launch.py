import os
import xacro
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_name = "my_car_description"
    pkg_share = FindPackageShare(package=pkg_name).find(pkg_name)
    urdf_xacro_path = os.path.join(pkg_share, "urdf", "my_car.urdf.xacro")

    robot_desc = xacro.process_file(urdf_xacro_path).toxml()
    use_sim_time = "true"

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time, "robot_description": robot_desc}]
    )

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        output="screen",
        arguments=["-topic", "robot_description", "-entity", "fishbot"]
    )

    return LaunchDescription([
        robot_state_publisher,
        spawn_entity
    ])