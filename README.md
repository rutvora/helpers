# Summary

This repo contains some helper functions and structs to be used in general for system research/analysis. You can include
the
relevant headers in your program for use.

Below are the descriptions of the helpers

## Channel

This is a naive implementation of channels from Go. They are used for simple inter-thread communication.
By default, the channels are unlimited in size and the underlying data-structure scales up as need be. You can use any
class or data-type within this channel.

You can optionally limit the maximum size of the channel.

_Note: This data structure is thread-safe and multiple threads can operate on it. However, ordering the access (
read/write) amongst multiple producers/consumers is left to the user_

Usage:

```c++
Channel<int> unlimitedChannel{};  // Grows with more data
Channel<CustomClass, 5> limitedChannel{}; // Maximum 5 units of data allowed
// From thread 1:
int toSend = 100;
unlimitedChannel << toSend;

// From thread 2:
int receive;
unllimitedChannel >> receive;   // This blocks until thread 1 sends some data (i.e. there is data to read)
```

## CPU

This library can be used for running processes in isolated CPU cores:

### Pre-requisites

1. Isolate at least 2 CPU cores from the Linux scheduler. We isolate cores 8-15 (8 cores) in the example below:

```text
This is for Ubuntu 22.04 with a grub bootloader. If you are running a different OS, modify accordingly

Isolate the CPUs from the linux scheduler (this maybe only isolates user-space applications)
Open `/etc/default/grub` in a text editor of your choice
Add `isolcpus=8-15` and `systemd.unified_cgroup_hierarchy=false` to the `GRUB_CMDLINE_LINUX_DEFAULT` variable
Run `sudo update-grub` to update the grub configuration

# Reboot the system and check if `cat /proc/cmdline` has `isolcpus=8-15` at the end.
```

2. Disable all possible interrupts on those cores

```text
Isolate the CPUs from irqbalance (so that no interrupts are served by the specified cores)
Open `/etc/default/irqbalance` in a text editor of your choice
Add `IRQBALANCE_BANNED_CPULIST=8-15` to the file
Run `sudo systemctl restart irqbalance` to restart the irqbalance service
```

3. Move all tasks (including possible kthreads) out of the isolated cores (need to do this once after every boot)

```bash
cset shield -c 8-15 -k on
# Grant the users of group <GROUP> to access the shield for running the experiments there
chgrp <GROUP> -R /sys/fs/cgroup/cpuset/user/
chmod -R 775 /sys/fs/cgroup/cpuset/user/

# You can reset the shield later by running the following (commented) command:
# cset shield --reset
```

4. Fix the CPU frequency on the specified cores, to reduce variability. Here, we fix it at 2.3GHz
   (need to do this once after every boot)

```bash
# Run this script with sudo
for i in {8..15}; do
  cpufreq-set -c $i -f 2.3GHz
done
```

### Using the library

```c++
// Move the current process to the CSet shield set up in step #3
CPU::movetoCSetShield();

// Move the current thread to a specific core or a group of cores
std:vector<uint8_t> cores{ 8, 9 };
CPU::setCPUAffinity(cores);
```

## Log

This class helps you log the output to the specified file (defaults to stderr)
Usage:

```c++
Logging log{Logging::WARN, "file.log"}; // Print all warnings or errors, but not debug messages
log.log(Logging::ERROR, "identifier", "message"); // This will print to file.log
log.log(Logging::DEBUG, "identifier", "message"); // This won't print to file.log
```

## Profile

This template allows you to supply any function to profile (get the runtime of)
Usage:

```c++
auto result = Profile::profile<ReturnType>(Function func, Args... args);
result.first; // Time taken to run this
result.second; // The output from the function
```

_Note: Currently, the default timer used is `std::chrono::steady_clock`. However, `high_resolution_clock` and `rdtscp`
are available. You can change the default timer() function in Profile.h if need be_

## Stats

This class instance can be used to record the statistics of any numeric data type.
Currently supported statistics are: Avg, Stdev, Min and Max (and their indices).
They also record the total number of inputs, and optionally store all the inputs.
You can also choose to ignore the initial 'n' entries (warm-up phase of your code)

Usage

```c++
Stats<int> stats{"nanoseconds", 1e2, true, 1e7}; // Unit: "nanoseconds", "ignoreInitial": 100, "storeVals": true, "expectedVals": 1e7
stats.update(5);  // Update with single value
std::vector<int> values{1, 2, 3};
stats.update(values); // Update with multiple values
```