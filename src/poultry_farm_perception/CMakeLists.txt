cmake_minimum_required(VERSION 3.8)
project(poultry_farm_perception)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(PROGRAMS
  scripts/static_pointcloud_fusion_node.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  rviz
  scripts
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
