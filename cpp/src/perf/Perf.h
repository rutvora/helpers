//
// Created by rutvora on 4/18/24.
//

#ifndef HELPERS_PERF_H
#define HELPERS_PERF_H

#define rdpmc(counter, low, high)         \
  asm volatile("rdpmc"                    \
               : "=a"(low), "=d"(high)    \
               : "c"(counter))

#define ASM_RDPMC(counter, low, high) \
  "mov %[" #counter "], %%ecx\n"      \
  "rdpmc\n"                           \
  "mov %%eax, %[" #low "]\n"          \
  "mov %%edx, %[" #high "]\n"

#include "iostream"
#include "linux/perf_event.h"
#include <sys/ioctl.h>
#include <asm/unistd.h>
#include <cstring>
#include <unistd.h>

/**
 * Template wrapper around Linux perf
 * @tparam Type Type of the event. One of the following:
 * PERF_TYPE_HARDWARE, PERF_TYPE_SOFTWARE, PERF_TYPE_TRACEPOINT, PERF_TYPE_HW_CACHE, PERF_TYPE_RAW, PERF_TYPE_BREAKPOINT
 * @tparam Config The event you want to measure. One of the following:
 * PERF_COUNT_HW_CPU_CYCLES, PERF_COUNT_HW_INSTRUCTIONS, PERF_COUNT_HW_CACHE_REFERENCES, PERF_COUNT_HW_CACHE_MISSES,
 * PERF_COUNT_HW_BRANCH_INSTRUCTIONS, PERF_COUNT_HW_BRANCH_MISSES, PERF_COUNT_HW_BUS_CYCLES,
 * PERF_COUNT_HW_STALLED_CYCLES_FRONTEND, PERF_COUNT_HW_STALLED_CYCLES_BACKEND, PERF_COUNT_HW_REF_CPU_CYCLES,
 * PERF_COUNT_SW_CPU_CLOCK, PERF_COUNT_SW_TASK_CLOCK, PERF_COUNT_SW_PAGE_FAULTS, PERF_COUNT_SW_CONTEXT_SWITCHES,
 * PERF_COUNT_SW_CPU_MIGRATIONS, PERF_COUNT_SW_PAGE_FAULTS_MIN, PERF_COUNT_SW_PAGE_FAULTS_MAJ,
 * PERF_COUNT_SW_ALIGNMENT_FAULTS, PERF_COUNT_SW_EMULATION_FAULTS, PERF_COUNT_SW_DUMMY, PERF_COUNT_HW_CACHE_L1D,
 * PERF_COUNT_HW_CACHE_L1I, PERF_COUNT_HW_CACHE_LL, PERF_COUNT_HW_CACHE_DTLB, PERF_COUNT_HW_CACHE_ITLB,
 * PERF_COUNT_HW_CACHE_BPU, PERF_COUNT_HW_CACHE_NODE, PERF_COUNT_HW_CACHE_OP_READ, PERF_COUNT_HW_CACHE_OP_WRITE,
 * PERF_COUNT_HW_CACHE_OP_PREFETCH
 * @tparam excludeKernel Whether to exclude time spent in the kernel or not
 * @tparam cpu -1 for all CPUs, or the CPU number to measure
 */
template<__u32 Type, __u64 Config, bool excludeKernel, int cpu>
class Perf {
 private:
  static Perf *perf;
  uint32_t low, high;
  perf_event_attr perfEventAttr{};
  int perfFileDescriptor;

  Perf();
  ~Perf();
  static long perfEventOpen(struct perf_event_attr *event, pid_t pid, int group_fd, unsigned long flags);
 public:
  Perf(Perf &other) = delete;
  void operator=(const Perf &) = delete;

  /**
   * Get the singleton instance of the Perf class
   * @return The instance of perf class
   */
  static Perf *getInstance();

  /**
   * Reset the performance counter
   */
  void reset();

  /**
   * Enable the performance counter (costs an ioctl)
   */
  void enable();

  /**
   * Disable the performance counter (costs an ioctl)
   */
  void disable();

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wattributes"

  [[gnu::always_inline]] [[clang::always_inline]]
  inline uint64_t readCounter() {
    rdpmc(Config, low, high);
    return ((uint64_t) high << 32) | low;
  }
#pragma GCC diagnostic pop

};

#include "Perf.tpp"

#endif //HELPERS_PERF_H
