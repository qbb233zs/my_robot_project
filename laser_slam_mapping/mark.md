# ROS2激光雷达SLAM建图项目说明文档

## 一、项目简介

本项目基于ROS2 Humble + Gazebo仿真环境，完成了差速驱动机器人模型（mybot）搭建、仿真激光雷达传感器配置、底层运动控制与里程计发布，最终使用 slam_toolbox 实现了室内环境的二维激光SLAM建图，完成了从环境搭建、传感器调试、问题排查到地图构建与保存的全流程，生成的地图可直接用于后续NAV2自主导航任务。

---

## 二、环境依赖

依赖项 版本/说明
操作系统 Ubuntu 22.04 LTS
ROS2版本 Humble Hawksbill
仿真环境 Gazebo 11 (ROS2 Humble内置版本)
核心ROS2依赖包 slam_toolbox、nav2-map-server、robot_state_publisher、gazebo_ros_pkgs、tf2-tools、teleop-twist-keyboard

ROS2安装与环境配置参考：

· ROS2安装指南
· ROS2环境配置

---

## 三、核心实现内容

### 1. 仿真机器人模型搭建

基于URDF/Xacro格式搭建了两轮差速驱动机器人模型（mybot），模型包含：

· 机器人基坐标系 base_link，里程计坐标系 odom，激光雷达坐标系 laser_link；
· 轮子与机身的碰撞与物理属性配置；
· 完整的关节与link层级结构，保证TF坐标变换链路完整。

### 2. 仿真激光雷达传感器配置

在机器人模型中集成了Gazebo激光雷达仿真插件，核心配置如下：

· 水平扫描范围 360°，采样点数 360个，角度分辨率 1°；
· 有效测距范围：0.12m ~ 8.0m。

### 3. 底层运动控制与里程计实现

放弃了存在配置冗余的 ros2_control 框架，改用 Gazebo 原生插件实现底层控制，保证了仿真的稳定性和轻量化：

· 集成 libgazebo_ros_diff_drive.so 差速驱动插件，订阅ROS2标准控制话题 /cmd_vel，实现机器人的前进、转向运动控制；
· 插件自动发布里程计话题 /odom，并发布 odom -> base_link 的 TF 坐标变换，为 SLAM建图提供基础里程计信息；
· 集成 libgazebo_ros_joint_state_publisher.so 关节状态发布插件，发布轮子关节状态，保证机器人模型TF树完整。

---

## 四、开发过程中遇到的核心问题与解决方案

### 1. ros2_control残留配置导致的启动报错

现象：启动Gazebo仿真launch文件时，终端持续报 waiting for service /controller_manager/load_controller to become available 错误，部分进程直接崩溃退出。

根因：初始的launch文件和URDF模型中，残留了 ros2_control 框架的控制器加载代码与配置，但并未启动对应的 controller_manager 节点，也没有完成 ros2_control 的完整配置，导致节点启动时持续等待不存在的服务，最终报错崩溃。

解决方案：

· 彻底清理launch文件中所有与 ros2_control 相关的加载代码；
· 改用Gazebo原生差速插件，弃用冗余的 ros2_control 框架。

### 2. SLAM建图严重漂移、地图重影错位

现象：控制机器人移动过程中，RViz中构建的地图出现严重的重影、错位，机器人位姿跑偏，建图结果完全不可用。

根因：

1. 仿真时间不同步：robot_state_publisher 节点未开启 use_sim_time 参数，启动SLAM节点时也未开启仿真时间，导致Gazebo、机器人状态发布、SLAM算法各节点的时间戳不统一，TF变换和激光数据的时间错乱，SLAM算法位姿计算完全错误。
2. 里程计误差累积过快：使用键盘控制时，默认的线速度、角速度过大，机器人转弯过急、频繁加减速，导致差速里程计的误差快速累积，SLAM算法无法正确匹配激光帧。

解决方案：

· 在所有涉及仿真时间的节点（robot_state_publisher、slam_toolbox）的启动参数中，统一设置 use_sim_time 为 True；
· 调整键盘控制的速度，使用较小的线速度（≤0.2 m/s）和角速度（≤0.5 rad/s），平稳移动机器人。

### 3. 激光雷达参数不匹配的警告问题

现象：启动 slam_toolbox 节点时，终端出现 minimum laser range setting (0.0 m) exceeds the capabilities of the used Lidar (0.1 m)、maximum laser range setting (20.0 m) exceeds the capabilities of the used Lidar (8.0 m) 的警告。

根因：slam_toolbox 的默认配置参数与仿真激光雷达实际配置的测距范围不匹配，算法默认的最小测距 0m、最大测距 20m，超出了激光雷达 0.12m~8m 的有效范围。

解决方案：

· 在启动SLAM节点时通过参数显式指定激光雷达的有效范围：laser_min_range:=0.12 和 laser_max_range:=8.0，警告即可消除。

### 4. TF树断裂、坐标变换找不到的问题

现象：RViz 中无法显示机器人模型、激光雷达扫描数据，报错 Could not transform from [laser_link] to [map]，找不到对应坐标系的变换关系。

根因：

1. URDF 模型中激光雷达的 link 名、轮子的关节名，与插件中配置的名称不一致，导致插件无法发布正确的关节状态和 TF 变换；
2. 差速驱动插件未开启 TF 发布开关，导致 odom -> base_link 的变换缺失，TF 链路断裂。

解决方案：

1. 核对 URDF 中所有关节、link 的名称，保证激光雷达插件、差速驱动插件中配置的关节名、frame_id，与 URDF 中的定义完全一致；
2. 在差速驱动插件的配置中，明确开启 <publish_odom>true</publish_odom>、<publish_odom_tf>true</publish_odom_tf>，保证里程计和对应的 TF 变换正常发布；
3. 通过 ros2 run tf2_tools view_frames 工具查看完整 TF 树，快速定位断裂的链路，针对性修复。

## 五、项目文件结构
```bash
laser_slam_mapping/         # 项目根目录
├── src/                     # ROS2功能包源码目录
│   ├── mybot_description/   # 机器人模型描述功能包
│   │   ├── config/          # 配置文件目录
│   │   │   └── mybot_ros2_controller.yaml  # 控制器配置文件
│   │   ├── include/         # 头文件目录
│   │   │   └── mybot_description/
│   │   ├── launch/          # 启动文件目录
│   │   │   ├── display_robot.launch.py      # 机器人模型可视化启动文件
│   │   │   └── gazebo_sim.launch.py         # Gazebo仿真环境启动文件
│   │   ├── src/             # 功能包源码目录
│   │   ├── urdf/            # 机器人URDF模型目录
│   │   │   └── mybot/       # 机器人模型组件合集
│   │   │       ├── actuator/                # 运动执行器模型
│   │   │       │   ├── caster.urdf.xacro    # 万向轮模型
│   │   │       │   └── wheel.urdf.xacro     # 差速驱动轮模型
│   │   │       ├── plugins/                 # Gazebo仿真插件配置
│   │   │       │   ├── gazebo_control_plugin.xacro  # 差速驱动控制器插件
│   │   │       │   └── gazebo_sensor_plugin.xacro   # 传感器仿真插件
│   │   │       ├── sensor/                  # 传感器模型
│   │   │       │   ├── camera.urdf.xacro    # 相机模型
│   │   │       │   ├── imu.urdf.xacro       # IMU惯性测量单元模型
│   │   │       │   └── laser.urdf.xacro     # 2D激光雷达模型
│   │   │       ├── base.urdf.xacro          # 机器人基座主体模型
│   │   │       ├── common_inertia.xacro     # 通用惯性参数宏定义
│   │   │       ├── mybot_ros2_control.xacro # ros2_control控制器配置
│   │   │       ├── mybot.urdf.xacro         # 机器人主模型文件
│   │   │       └── first_robot.xacro        # 早期原型模型备份
│   │   ├── world/           # 仿真环境世界文件目录
│   │   │   └── room/        # 自定义室内场景
│   │   │       ├── model.config
│   │   │       ├── model.sdf
│   │   │       └── custom_room.world  # 自定义仿真世界文件
│   │   ├── CMakeLists.txt   # 功能包编译规则文件
│   │   └── package.xml      # 功能包元信息与依赖声明文件
│   │
│   └── mybot_navigation2/   # 导航与SLAM建图功能包
│       ├── include/         # 头文件目录
│       │   └── mybot_navigation2/
│       ├── maps/            # SLAM建图结果存放目录
│       │   ├── my_fishbot_map.pgm   # 栅格地图图片文件
│       │   └── my_fishbot_map.yaml  # 地图配置元数据文件
│       ├── src/             # 功能包源码目录
│       ├── CMakeLists.txt   # 功能包编译规则文件
│       └── package.xml      # 功能包元信息与依赖声明文件
│
└── mark.md                  # 本项目说明文档
```

## 六、完整运行与建图步骤

### 1. 环境准备与编译

```bash
# 安装所有依赖包
sudo apt update
sudo apt install -y ros-humble-slam-toolbox ros-humble-nav2-map-server ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-tf2-tools

# 进入工作空间编译
cd ~/mybot_ws
colcon build --packages-select mybot_description mybot_navigation2
source install/setup.bash
```

### 2. 启动 Gazebo 仿真环境

新开终端执行：

```bash
cd ~/mybot_ws
source install/setup.bash
# 杀掉残留进程，避免干扰
pkill -9 gzserver gzclient ros2
# 启动仿真（使用自定义世界）
ros2 launch mybot_description gazebo_sim.launch.py
```

正常启动后，Gazebo 窗口会打开，机器人模型加载在 custom_room.world 环境中，终端无红色报错，差速插件、激光雷达插件正常初始化。

### 3. 启动 SLAM 建图节点

新开终端执行：

```bash
cd ~/mybot_ws
source install/setup.bash
# 启动SLAM，必须开启仿真时间，同时匹配雷达量程参数
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true laser_min_range:=0.12 laser_max_range:=8.0
```

正常启动后，终端输出 Mapper node started，无报错，SLAM节点开始运行。

### 4. 启动 RViz 可视化建图过程

新开终端执行：

```bash
# 启动 RViz，使用导航自带的配置文件，直接显示地图、机器人、激光数据
rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz
```

正常启动后，RViz窗口可看到机器人模型、激光扫描点云，随着机器人移动会逐步生成栅格地图。

### 5. 启动键盘控制，完成环境扫描

新开终端执行，使用低速参数保证建图稳定：

```bash
cd ~/mybot_ws
source install/setup.bash
# 启动低速键盘控制，降低线速度和角速度
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p linear_scale:=0.15 -p angular_scale:=0.2
```

按照终端提示控制机器人移动，缓慢遍历整个仿真环境，让激光雷达扫描到所有墙面与障碍物，完成完整地图的构建。

### 6. 保存建好的地图

当地图构建完成，无明显错误后，新开终端执行：

```bash
cd ~/mybot_ws
source install/setup.bash
# 保存地图，生成 yaml 和 pgm 文件到 mybot_navigation2/maps 目录
ros2 run nav2_map_server map_saver_cli -f ~/mybot_ws/src/mybot_navigation2/maps/my_fishbot_map
```

终端输出 Map saved successfully 即完成地图保存，生成的地图文件（my_fishbot_map.pgm 和 my_fishbot_map.yaml）可直接用于后续的自主导航任务。

## 七、项目成果

### 1. 完成了仿真机器人、激光雷达、运动控制的全流程配置，解决了开发过程中遇到的框架兼容、时间同步、TF变换等各类问题，搭建了稳定可用的ROS2机器人仿真环境。
### 2. 成功使用 slam_toolbox 完成了室内环境的二维 SLAM 建图，生成了完整、无漂移、无重影的栅格地图。