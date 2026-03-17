cmake_minimum_required(VERSION 3.5)
project(mybot_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 找依赖包
find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  # 下面这行跳过cpplint检查（仅在git仓库里生效，当你给所有源文件加了版权和许可证后可以注释掉）
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# 安装所有资源文件夹，保证launch、urdf、world、config都能被找到
install(DIRECTORY launch urdf config world
  DESTINATION share/${PROJECT_NAME}
)

ament_package()