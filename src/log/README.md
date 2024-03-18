## Log

This class helps you log the output to the specified file (defaults to stderr)
Usage:

```c++
Logging log{Logging::WARN, "file.log"}; // Print all warnings or errors, but not debug messages to file.log
// Logging log{Logging::WARN}; // Print all warnings or errors, but not debug messages to stderr
log.log(Logging::ERROR, "message", "identifier"); // This will print to file.log
log.log(Logging::ERROR, "message");               // This will print to file.log (no identifier string)
log.log(Logging::DEBUG, "message", "identifier"); // This will NOT print to file.log
```

The output would be of the form:

```
file_name:line_num [time_from_log_init: error_level] identifier message
```