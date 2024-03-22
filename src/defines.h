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
#define TIMER_RDTSCP timerRdtscp
#define TIMER_STEADY_CLOCK timerSteadyClock
#define TIMER_HIGH_RES_CLOCK timerHighResClock
#define TIMER_RDTSC timerRdtsc
#define TIMER_RDPRU timerRdpru
#define TIMER_ARMV8 timerArmV8

// Fences
#define TIMER_SERIALIZE _cpuid // _serialize is better alternative (intrinsic) that can be used (only available on Intel 12th Gen and later)
#define TIMER_LFENCE _mm_lfence
#define TIMER_MFENCE _mm_mfence
#define TIMER_SFENCE _mm_sfence

#endif