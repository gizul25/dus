cmake_minimum_required(VERSION 3.14)
project(height_control LANGUAGES CXX)

include(FetchContent)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.14.0
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(googletest)

add_library(height_control height_control.cpp)
target_include_directories(height_control PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

enable_testing()
add_executable(height_control_tests tests/height_control_test.cpp)
target_link_libraries(height_control_tests PRIVATE height_control GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(height_control_tests)
