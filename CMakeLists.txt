cmake_minimum_required(VERSION 3.22)

# Disable in-source builds to prevent source tree corruption.
if ("${CMAKE_SOURCE_DIR}" STREQUAL "${CMAKE_BINARY_DIR}")
    message(FATAL_ERROR
            "FATAL: In-source builds are not allowed. You should create a separate directory for build files.")
endif ()
set(CMAKE_DISABLE_IN_SOURCE_BUILD ON CACHE INTERNAL "Disallow building in the source directory")
set(CMAKE_DISABLE_SOURCE_CHANGES ON CACHE INTERNAL "Disallow building in the source directory")

include(CMakeDependentOption)
project(helpers CXX C)

set(CMAKE_CXX_STANDARD 23 CACHE INTERNAL "")

if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif ()

# CXX Flags
set(CMAKE_CXX_FLAGS "-Wall -Wextra -Wno-unknown-pragmas" CACHE INTERNAL "")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0" CACHE INTERNAL "")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-g -O3" CACHE INTERNAL "")
set(CMAKE_CXX_FLAGS_RELEASE "-O3" CACHE INTERNAL "")

add_compile_definitions(
        LOG_LEVEL_ERROR=0
        LOG_LEVEL_WARN=1
        LOG_LEVEL_DEBUG=2
)

if (CMAKE_BUILD_TYPE MATCHES Debug)
    add_compile_definitions(LOG_VERBOSITY=LOG_LEVEL_DEBUG)
    message("Building Debug")
else ()
    add_compile_definitions(LOG_VERBOSITY=LOG_LEVEL_ERROR)
    message("Building Release")
endif ()

include_directories(src src/channel src/cpu src/log src/profile src/stats src/perf)

add_subdirectory(src)
add_subdirectory(tests)
