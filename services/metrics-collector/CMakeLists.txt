cmake_minimum_required(VERSION 3.15)
project(metrics-collector CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(include)

# Source files
file(GLOB_RECURSE SOURCES "src/*.cpp")

# Executable target
add_executable(metrics-collector main.cpp ${SOURCES})

# Target compiler flags
if(MSVC)
    target_compile_options(metrics-collector PRIVATE /W4 /WX)
else()
    target_compile_options(metrics-collector PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()
