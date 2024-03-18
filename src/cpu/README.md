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