## Sys

This library provides wrappers around the system functionalities. Currently, the following functionalities are
available:

- `std::string run(std::string &cmd, bool stdout, bool stderr)`: Runs the given command as a child process, and returns the stdout of the command
  as a string (you can use `cmd 2>&1` to redirect stderr to stdout and get that in the output)  

```C++
std::string command = "ls -l";
// To print only stdout
auto output = run(command, true, false);

// To print stderr and stdout
auto output = run(command, true, true);
```