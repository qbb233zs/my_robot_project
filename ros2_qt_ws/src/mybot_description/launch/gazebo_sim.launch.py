import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
import os
import launch_ros.parameter_descriptions

def generate_launch_description():
    # 获取功能包的共享路径
    urdf_package_path = get_package_share_directory('mybot_description')
    default_xacro_path = os.path.join(urdf_package_path, 'urdf', 'mybot/mybot.urdf.xacro')
    default_gazebo_world_path = os.path.join(urdf_package_path, 'world', 'custom_room.world')

    # 声明模型路径参数，方便后续修改
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value=str(default_xacro_path),
        description='加载的机器人模型文件路径'
    )

    # 执行xacro命令解析模型，转换为URDF内容，供状态发布器使用
    substitutions_command_result = launch.substitutions.Command(
        ['xacro ', launch.substitutions.LaunchConfiguration('model')]
    )
    robot_description_value = launch_ros.parameter_descriptions.ParameterValue(
        substitutions_command_result,
        value_type=str
    )

    # 启动机器人状态发布器，发布机器人模型和TF变换
    action_robot_state_publisher = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_value,
            'use_sim_time': True  # 关键修复：开启仿真时间
        }]
    )

    # 启动Gazebo仿真环境，加载自定义的world地图
    action_launch_gazebo = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            [get_package_share_directory('gazebo_ros'), '/launch/', 'gazebo.launch.py']
        ),
        launch_arguments={
            'world': default_gazebo_world_path,
            'verbose': 'true'
        }.items()
    )

    # 将机器人模型加载进Gazebo场景
    action_spawn_entity = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', '/robot_description', '-entity', 'mybot'],
        output='screen'
    )

    # 按顺序启动所有节点，保证运动逻辑正确
    return launch.LaunchDescription([
        action_declare_arg_mode_path,
        action_robot_state_publisher,
        action_launch_gazebo,
        action_spawn_entity,
    ])