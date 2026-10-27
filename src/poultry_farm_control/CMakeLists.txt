cmake_minimum_required(VERSION 3.8)
project(poultry_farm_control)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(PROGRAMS
  scripts/amr_teleop_keyboard.py
  scripts/poultry_inspection_controller.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  config
  scripts
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
