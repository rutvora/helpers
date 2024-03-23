//
// Created by rutvora on 1/22/24.
//

#ifndef HELPER_DEFINES_H

/*
 * Defines for Profiling functions
 */
#define TIMER_FEATURE_OFF 0
#define TIMER_FEATURE_ON 1

// Timers
#define TIMER_STEADY_CLOCK timerSteadyClock
#define TIMER_HIGH_RES_CLOCK timerHighResClock
#if defined(__x86_64__) || defined(_M_AMD64)
#define TIMER_RDTSCP timerRdtscp
#define TIMER_RDTSC timerRdtsc
#define TIMER_RDPRU timerRdpru
#elif defined(__arm__) || defined(__aarch64__)
#define TIMER_ARMV8 timerArmV8
#endif

// Fences
#if defined(__x86_64__) || defined(_M_AMD64)
#define TIMER_SERIALIZE _cpuid // _serialize is better alternative (intrinsic) that can be used (only available on Intel 12th Gen and later)
#define TIMER_LFENCE _mm_lfence
#define TIMER_MFENCE _mm_mfence
#define TIMER_SFENCE _mm_sfence
#elif defined(__arm__) || defined(__aarch64__)
#define TIMER_SERIALIZE() __asm__ __volatile__ ("dsb sy\n isb sy" ::: "memory")
#define TIMER_LFENCE() __asm__ __volatile__ ("dmb ld" ::: "memory")
#define TIMER_MFENCE() __asm__ __volatile__ ("dmb sy" ::: "memory")
#define TIMER_SFENCE() __asm__ __volatile__ ("dmb st" ::: "memory")
#endif

#endif