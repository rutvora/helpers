//
// Created by rutvora on 10/31/23.
//

#ifndef HELPERS_PROFILE_H_
#define HELPERS_PROFILE_H_

#include <utility>
#include <cstdint>
#include <chrono>
#include <functional>
#include <concepts>

#ifdef _MSC_VER
#include "intrin.h"
#else
#include "x86intrin.h"
#endif

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

// Timer specific variables (do not change)
#define RDPRU_ECX_APERF    1          /* Use APERF register in RDRPU */

#ifndef PROFILE_TIMER
#define PROFILE_TIMER TIMER_RDTSCP
#endif

namespace Profile {
// Validate that the function pointer is valid and returns the necessary type
template<typename ReturnType, typename Func, typename... Args>
concept validFunctionWithRet = requires(Func &function, Args &... args) {
  { function(args...) } -> std::convertible_to<ReturnType>;
};

template<typename Func, typename... Args>
concept validFunctionWithoutRet = requires(Func &function, Args &... args) {
  { function(args...) };
};

// Timers
[[maybe_unused]] inline auto timerSteadyClock() {
#if TIMER_MEM_FENCE == TIMER_FEATURE_ON
  _mm_mfence();
#endif
  return std::chrono::steady_clock::now();
}

[[maybe_unused]] inline auto timerHighResClock() {
#if TIMER_MEM_FENCE == TIMER_FEATURE_ON
  _mm_mfence();
#endif
  return std::chrono::high_resolution_clock::now();
}

[[maybe_unused]] inline auto timerRdtscp() {
  uint32_t low = 0, high = 0;
  asm volatile(
      "rdtscp\n"
      : "=a" (low)
#if TIMER_32_BIT != TIMER_FEATURE_ON
      , "=d" (high)
#endif
      :
      : "ecx" // CPUID, which we want to ignore
      );

#if TIMER_32_BIT == TIMER_FEATURE_ON
  return low;
#else
  return ((uint64_t)high << 32) | low;
#endif
}

[[maybe_unused]] inline auto timerRdtsc() {
  uint32_t low = 0, high = 0;
#if TIMER_MEM_FENCE == TIMER_FEATURE_ON
  _mm_mfence();
#endif
  asm volatile("rdtsc\n"
               : "=a"(low)
#if TIMER_32_BIT != TIMER_FEATURE_ON
               , "=d"(high)
#endif
               );
#if TIMER_32_BIT == TIMER_FEATURE_ON
  return low;
#else
  return ((uint64_t)high << 32) | low;
#endif
}

[[maybe_unused]] inline auto timerRdpru() {
  uint32_t low = 0, high = 0;
#if TIMER_MEM_FENCE == TIMER_FEATURE_ON
  _mm_mfence();
#endif
  asm volatile(
      "rdpru\n"
      : "=a"(low)
#if TIMER_32_BIT != TIMER_FEATURE_ON
      , "=d"(high)
#endif
      : "c"(RDPRU_ECX_APERF)
      );
#if TIMER_32_BIT == TIMER_FEATURE_ON
  return low;
#else
  return ((low) | (uint64_t) (high) << 32);
#endif
}

#if PROFILE_TIMER == TIMER_RDTSCP
constexpr auto timer = timerRdtscp;
#elif PROFILE_TIMER == TIMER_STEADY_CLOCK
constexpr auto timer = timerSteadyClock;
#elif PROFILE_TIMER == TIMER_HIGH_RES_CLOCK
constexpr auto timer = timerHighResClock;
#elif PROFILE_TIMER == TIMER_RDTSC
constexpr auto timer = timerRdtsc;
#elif PROFILE_TIMER == TIMER_RDPRU
constexpr auto timer = timerRdpru;
#else
#error "Invalid timer specified"
#endif

/**
 *
 * @tparam Func A function pointer
 * @tparam Args The arguments to the function referred by the function pointer
 * @param function The function to profile
 * @param args The arguments to be passed to the function to profile
 * @return Time taken to run the function, in ns
 */
template<typename ReturnType, typename Func, typename... Args>
requires validFunctionWithRet<ReturnType, Func, Args...>
std::pair<uint64_t, ReturnType> profile(const Func &function, Args &... args);

/**
 * Special case of the above function, when the function to profile does not return anything
 */
template<typename Func, typename... Args>
requires validFunctionWithoutRet<Func, Args...>
uint64_t profile(const Func &function, Args &... args);

};

// Include the definitions of the templated functions. Templates require that the types are known at compile time.
// A separate cpp file is an isolated compilation unit, which would not know what the templates should concrete to,
// when compiling in isolation. As such, the definitions are instead written to the tpp file and imported here to be
// transitively imported in whatever compilation unit (i.e. cpp or cu or c file) they are used in.
#include "Profile.tpp"

#endif //HELPERS_PROFILE_H_
