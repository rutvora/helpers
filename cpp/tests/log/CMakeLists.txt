add_executable(log_test log_test.cpp)
target_link_libraries(log_test log)
add_test(NAME LOG_TEST COMMAND log_test)