//
// Created by rutvora on 4/18/24.
//

#include "Perf.h"

template<__u32 Type, __u64 Config, bool excludeKernel, int cpu>
Perf<Type, Config, excludeKernel, cpu> *Perf<Type, Config, excludeKernel, cpu>::perf = nullptr;

template<__u32 Type, __u64 Config, bool excludeKernel, int cpu>
long Perf<Type, Config, excludeKernel, cpu>::perfEventOpen(struct perf_event_attr *event,
                                                           pid_t pid,
                                                           int group_fd,
                                                           unsigned long flags) {
  return syscall(__NR_perf_event_open, event, pid, cpu, group_fd, flags);
}

template<__u32 Type, __u64 Config, bool excludeKernel, int cpu>
Perf<Type, Config, excludeKernel, cpu> *Perf<Type, Config, excludeKernel, cpu>::getInstance() {
  if (perf == nullptr) {
    perf = new Perf();
  }
  return perf;
}

template<__u32 Type, __u64 Config, bool excludeKernel, int cpu>
Perf<Type, Config, excludeKernel, cpu>::Perf() {
  perfEventAttr.size = sizeof(struct perf_event_attr);
  perfEventAttr.disabled = 1; // Start out disabled
  perfEventAttr.exclude_idle = 1; // Don't count when CPU is idle
  perfEventAttr.exclude_hv = 1; // Don't count when in hypervisor
  perfEventAttr.exclude_kernel = excludeKernel; // Whether to exclude time spent in kernel
  perfEventAttr.type = Type;  // Type of event to count
  perfEventAttr.config = Config;  // Which event to count

  perfFileDescriptor = perfEventOpen(&perfEventAttr, 0, -1, 0);
  if (perfFileDescriptor == -1) {
      throw std::runtime_error("Error opening perf event");
  }
}

template<__u32 Type, __u64 Config, bool excludeKernel, int cpu>
Perf<Type, Config, excludeKernel, cpu>::~Perf() {
  close(perfFileDescriptor);
}

template<__u32 Type, __u64 Config, bool excludeKernel, int cpu>
void Perf<Type, Config, excludeKernel, cpu>::reset() {
  ioctl(perfFileDescriptor, PERF_EVENT_IOC_RESET, 0);
  ioctl(perfFileDescriptor, PERF_EVENT_IOC_ENABLE, 0);
}

template<__u32 Type, __u64 Config, bool excludeKernel, int cpu>
void Perf<Type, Config, excludeKernel, cpu>::enable() {
  ioctl(perfFileDescriptor, PERF_EVENT_IOC_ENABLE, 0);
}

template<__u32 Type, __u64 Config, bool excludeKernel, int cpu>
void Perf<Type, Config, excludeKernel, cpu>::disable() {
  ioctl(perfFileDescriptor, PERF_EVENT_IOC_DISABLE, 0);
}