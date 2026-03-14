# 任务一：基于Qt的ROS2小车指令发送界面
## 项目概述
本项目完成导航方向寒假任务一核心需求：通过Qt Designer设计可视化操作界面，将用户输入的自定义指令转换为ROS2标准控制指令，发布至仿真小车话题，实现对小车的精准操控。

## 环境依赖
| 依赖项 | 版本要求 |
|--------|----------|
| 操作系统 | Ubuntu 20.04 / 22.04 |
| ROS2版本 | Humble Hawksbill |
| Qt版本 | Qt 5.15.x |
| 编译工具 | colcon、CMake 3.16+ |
| 仿真环境 | fishbot 仿真模型 |

## 项目结构
ROS2_QT_WS/
└── src/
└── qt_robot_teleop/          # 本功能包根目录
├── include/qt_robot_teleop/
│   └── main_window.h     # Qt窗口头文件
├── src/
│   ├── main.cpp          # 程序入口文件
│   ├── main_window.cpp   # 界面逻辑+ROS2通信实现
│   └── main_window.ui    # Qt Designer可视化界面文件
├── CMakeLists.txt        # 编译配置文件（已完成Qt+ROS2联动）
├── package.xml           # ROS2功能包配置文件
└── README.md             # 本说明文档（你现在正在写的）
## 核心功能实现
### 1. Qt界面设计
通过Qt Designer完成界面布局，核心控件及功能：
- 输入框：`linear_x_edit`（线速度）、`angular_z_edit`（角速度）
- 按钮：`send_btn`（发送指令）、`stop_btn`（紧急停止）
- 日志框：`log_browser`（实时显示指令发布信息）

### 2. ROS2通信核心代码（main_window.cpp）
```cpp
#include "main_window.h"
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"

// 构造函数：初始化ROS2节点、话题发布者、绑定界面信号
MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent), ui(new Ui::MainWindow) {
    ui->setupUi(this);
    // 初始化ROS2
    rclcpp::init(0, nullptr);
    // 创建ROS2节点
    node_ = std::make_shared<rclcpp::Node>("qt_teleop_node");
    // 创建话题发布者（订阅话题与仿真小车一致）
    pub_ = node_->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    // 绑定按钮点击事件
    connect(ui->send_btn, &QPushButton::clicked, this, &MainWindow::send_control_cmd);
    connect(ui->stop_btn, &QPushButton::clicked, this, &MainWindow::stop_car);
}

// 析构函数：释放ROS2资源
MainWindow::~MainWindow() {
    rclcpp::shutdown();
    delete ui;
}

// 发送控制指令核心逻辑
void MainWindow::send_control_cmd() {
    // 获取界面输入的速度值（转换为浮点数）
    double linear_speed = ui->linear_x_edit->text().toDouble();
    double angular_speed = ui->angular_z_edit->text().toDouble();
    
    // 构建ROS2 Twist控制消息
    geometry_msgs::msg::Twist cmd_msg;
    cmd_msg.linear.x = linear_speed;   // 前后线速度
    cmd_msg.angular.z = angular_speed; // 左右角速度
    
    // 发布指令
    pub_->publish(cmd_msg);
    
    // 日志显示到界面
    ui->log_browser->append(QString("✅ 发送指令 -> 线速度：%1 m/s | 角速度：%2 rad/s")
                            .arg(linear_speed).arg(angular_speed));
}

// 紧急停止指令
void MainWindow::stop_car() {
    geometry_msgs::msg::Twist stop_msg;
    stop_msg.linear.x = 0.0;
    stop_msg.angular.z = 0.0;
    pub_->publish(stop_msg);
    ui->log_browser->append("🛑 发送停止指令，小车已紧急停止");
}
3. CMake关键配置（CMakeLists.txt）
cmake_minimum_required(VERSION 3.8)
project(qt_robot_teleop)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 启用Qt自动编译（核心：处理ui、h文件）
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# 查找ROS2依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# 查找Qt5依赖
find_package(Qt5 REQUIRED COMPONENTS Core Widgets)

# 生成可执行文件
add_executable(qt_teleop_node
  src/main.cpp
  src/main_window.cpp
  src/main_window.ui
)

# 链接ROS2库
ament_target_dependencies(qt_teleop_node
  rclcpp
  std_msgs
  geometry_msgs
)

# 链接Qt5库
target_link_libraries(qt_teleop_node
  Qt5::Core
  Qt5::Widgets
)

# 安装可执行文件
install(TARGETS
  qt_teleop_node
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
编译与运行步骤

1. 编译功能包

在终端进入工作空间根目录 ROS2_QT_WS，执行：
# 仅编译本功能包
colcon build --packages-select qt_robot_teleop
# 加载环境变量
source install/setup.bash
2. 启动仿真小车

新开终端，加载环境变量后启动仿真：
ros2 launch fishbot_description display.launch.py
3. 启动Qt控制界面

再开一个终端，执行：
ros2 run qt_robot_teleop qt_teleop_node
4. 操作说明

1. 在Qt界面输入框填数值（如线速度填0.2，角速度填0.5）；

2. 点击「发送指令」，仿真小车按指令运动；

3. 点击「停止小车」，小车立即停下；

4. 日志框会实时显示发送的指令信息。

注意事项

1. 话题名必须一致：Qt发布的/cmd_vel需与仿真小车订阅的话题名完全相同，否则小车无响应；

2. 输入校验：输入框仅支持数字（整数/小数），输入非数字会默认转换为0；

3. 编译报错：若提示Qt库未找到，执行sudo apt install qtbase5-dev安装依赖即可。