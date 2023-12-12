add_library(log STATIC log/Logging.cpp)
add_library(cpu STATIC cpu/CPU.cpp)
target_link_libraries(cpu log)