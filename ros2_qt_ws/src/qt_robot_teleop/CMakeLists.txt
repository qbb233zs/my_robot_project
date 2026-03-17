cmake_minimum_required(VERSION 3.8)
project(qt_robot_teleop)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Widgets)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)  
set(CMAKE_AUTORCC ON)

add_executable(qt_teleop_node
  src/main.cpp
  src/main_window.cpp
  src/main_window.ui  
)

ament_target_dependencies(qt_teleop_node
  rclcpp
  std_msgs
  geometry_msgs
)

target_link_libraries(qt_teleop_node
  Qt5::Widgets
  Qt5::Core
)

install(TARGETS
  qt_teleop_node
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()