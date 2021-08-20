cmake_minimum_required(VERSION 3.13.4)
project(VK)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS "-Wall -Wextra")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -lcurl -O2")
add_executable(VK main.cpp json.hpp web_crawler.hpp simple_vector.hpp graph.hpp profiler.hpp cmd_parser.hpp transparent_string.hpp)
target_link_libraries(VK curl)