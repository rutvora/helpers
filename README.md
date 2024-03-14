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

## Profile

This template allows you to supply any function to profile (get the runtime of)

**Usage:**

```c++
// Define the timer (defaults to TIMER_RDTSCP if undefined)
#define
PROFILE_TIMER TIMER_RDTSCP  // See below for available timers

// For functions with a return value
auto result = Profile::profile<ReturnType>(Function func, Args... args);
result.first; // Time taken to run this
result.second; // The output from the function

// For functions without a return value
auto result = Profile::profile(Function func, Args... args);
```

The following timers are available:

1. **TIMER_RDTSCP**:
   This is the DEFAULT timer. It uses the RDTSCP instruction available on x86 (or x86_64) processors.  
   RDTSCP (and RDTSC) rely on the TSC (Time Stamp Counter) register, which is incremented at a constant rate.
   However, if your CPU core is not at a fixed frequency (see the CPU section on how to fix it), RDTSC(P)
   results might fluctuate.  
   RDTSCP issues a serialising instruction to ensure that all memory operations before RDTSCP are executed before RDTSCP
   is triggered (which is not always the case on processors with out-of-order execution, which is all processors
   today)

_Note: ISSUES WITH AMD: AMD seems to increment the counter at a constant rate of the crystal clock frequency (usually
100MHz), but by a value dependend on the processor's base frequency (check processor specifications on the AMD
website for this information). So, for example, the AMD Ryzen 4800HS has a base clock of 2.9GHz, so all values read
by RDTSC(P) will be a multiple of 29!

2. **TIMER_RDTSC**:
   This timer is similar to RDTSC and has all of its benefits and losses, except that RDTSC does not ensure
   serialisation that RDTSCP does.
3. **TIMER_RDPRU**:
   This timer uses the RDPRU instruction avaliable on AMD hardware ONLY. RDPRU allows user-space programs to read the
   exact processor cycle count. As such, it does not have the issue that RDTSC(P) has on AMD processors. In addition, if
   you are measuring real cycle counts, this helps avoid setting the CPU core frequency (which requires root access).
4. **TIMER_STEADY_CLOCK**
   This timer is the `std::chrono::steady_clock::now()`
5. **TIMER_HIGH_RES_CLOCK**
   This timer is the `std::chrono::high_resolution_clock::now()`

### Features

Certain timers support certain additional features which can be turned on or off at compile time. All timer features
can be switched on (or off) using the value `TIMER_FEATURE_ON` (or `TIMER_FEATURE_OFF`)

```c++
TIMER_32_BIT TIMER_FEATURE_ON // Makes the timer 32-bit only
```

- **TIMER_32_BIT**: (DEFAULT = OFF, Applicable to RDTSC, RDTSCP, RDPRU) - Only read the lower 32 bits of the timer
  (avoids at least 1 extra CPU cycle by ignoring the higher bits). This is useful if you are only measuring timing
  difference, and the difference won't exceed 32 bits.  
  _Note: This can have an issue when the actual output from the timer instruction wraps around the lower 32 bits.
  However, this would happen rarely, and external code can be designed to handle this anomaly_
- **TIMER_FENCE**: (DEFAULT = ON, Applicable to RDTSC, RDPRU, STEADY_CLOCK, HIGH_RES_CLOCK) - Issue a FENCE before
  the timer. The type of fence is defined by `TIMER_FENCE_TYPE`.
- **TIMER_FENCE_TYPE**: (DEFAULT = `TIMER_SERIALIZE`). The following values are currently accepted:
    - **TIMER_SERIALIZE**: Uses the [`CPUID`](https://www.felixcloutier.com/x86/cpuid) instruction to ensure
      that all previous instructions finish executing and all loads/stores are complete.   
      _Note: A better instruction [`SERIALIZE`](https://www.felixcloutier.com/x86/serialize) is available on Intel
      processors from 12th gen onwards, and can be used by replacing the definition with `_serialize` (which is already
      an intrinsic)_
        - **TIMER_MFENCE**: Uses the [`MFENCE`](https://www.felixcloutier.com/x86/mfence) instruction to ensure all
          previous
          loads and stores are complete
    - **TIMER_SFENCE**: Uses the [`SFENCE`](https://www.felixcloutier.com/x86/sfence) instruction to ensure all previous
      stores are complete (loads may remain incomplete)
    - **TIMER_LFENCE**: Uses the [`LFENCE`](https://www.felixcloutier.com/x86/lfence) instruction to ensure all previous
      loads are complete (stores may remain incomplete)

## Stats

This class instance can be used to record the statistics of any numeric data type. Currently supported statistics are:
Avg, Stdev, Min and Max (and their indices). They also record the total number of inputs, and optionally store all the
inputs. You can also choose to ignore the initial 'n' entries (warm-up phase of your code)

Usage:

```c++
Stats<int> stats{"nanoseconds", 1e2, true, 1e7}; // Unit: "nanoseconds", "ignoreInitial": 100, "storeVals": true, "expectedVals": 1e7
stats.update(5);  // Update with single value
std::vector<int> values{1, 2, 3};
stats.update(values); // Update with multiple values
```