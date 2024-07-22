add_library(log STATIC log/Logging.cpp)
add_library(cpu STATIC cpu/CPU.cpp)
add_library(sys STATIC sys/Sys.cpp)
add_library(mutex STATIC mutex/Mutex.cpp)

target_link_libraries(sys log)
target_link_libraries(cpu sys mutex)