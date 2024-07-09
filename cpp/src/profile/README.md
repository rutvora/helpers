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
4. **TIMER_ARMV8**:
   This timer uses obtains the Counter-timer Virtual Count register. However, pre-ARMv8.6 processors update this at a
   system dependent rate of 1 - 50 MHz, ARMv8.6 and ARMv9.1 update it at
   1GHz [Source](https://developer.arm.com/documentation/102379/0103/What-is-the-Generic-Timer-?lang=en). Refer
   to [this](https://cpufun.substack.com/p/fun-with-timers-and-cpuid) on how to get the update frequency for your
   system.
5. **TIMER_STEADY_CLOCK**
   This timer is the `std::chrono::steady_clock::now()`
6. **TIMER_HIGH_RES_CLOCK**
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
    - **TIMER_SERIALIZE**: Uses the [`CPUID`](https://www.felixcloutier.com/x86/cpuid) instruction on amd64, and a
      combination
      of [`DSB SY` and `ISB SY`](https://developer.arm.com/documentation/dui0802/b/A32-and-T32-Instructions/DMB--DSB--and-ISB)
      on arm to ensure that all previous instructions finish executing and all loads/stores are complete.  
      _Note: A better instruction [`SERIALIZE`](https://www.felixcloutier.com/x86/serialize) is available on Intel
      processors from 12th gen onwards, and can be used by replacing the definition with `_serialize` (which is already
      an intrinsic)_
        - **TIMER_MFENCE**: Uses the [`MFENCE`](https://www.felixcloutier.com/x86/mfence) instruction on amd64
          and [`DMB SY`](https://developer.arm.com/documentation/dui0802/b/A32-and-T32-Instructions/DMB--DSB--and-ISB)
          on arm to ensure all previous loads and stores are complete.
    - **TIMER_SFENCE**: Uses the [`SFENCE`](https://www.felixcloutier.com/x86/sfence) instruction on amd64
      and [`DMB ST`](https://developer.arm.com/documentation/dui0802/b/A32-and-T32-Instructions/DMB--DSB--and-ISB) on
      arm to ensure all previous stores are complete (loads may remain incomplete)
    - **TIMER_LFENCE**: Uses the [`LFENCE`](https://www.felixcloutier.com/x86/lfence) instruction on amd64
      and [`DMB LD`](https://developer.arm.com/documentation/dui0802/b/A32-and-T32-Instructions/DMB--DSB--and-ISB) on
      arm to ensure all previous loads are complete (stores may remain incomplete)
