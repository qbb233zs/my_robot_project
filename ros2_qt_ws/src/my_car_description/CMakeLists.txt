cmake_minimum_required(VERSION 3.8)
project(my_car_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找必须的依赖
find_package(ament_cmake REQUIRED)
find_package(urdf REQUIRED)
find_package(xacro REQUIRED)

# 安装launch和urdf文件夹，这是ROS2能找到包的核心
install(DIRECTORY
  launch
  urdf
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()