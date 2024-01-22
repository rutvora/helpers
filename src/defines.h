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
#define TIMER_RDTSCP 1
#define TIMER_STEADY_CLOCK 2
#define TIMER_HIGH_RES_CLOCK 3
#define TIMER_RDTSC 4
#define TIMER_RDPRU 5

// Timer Features
#ifndef TIMER_32_BIT
#define TIMER_32_BIT TIMER_FEATURE_OFF
#endif

#ifndef TIMER_MEM_FENCE
#define TIMER_MEM_FENCE TIMER_FEATURE_ON
#endif

#endif