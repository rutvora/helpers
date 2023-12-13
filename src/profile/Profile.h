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
  return std::chrono::steady_clock::now();
}

[[maybe_unused]] inline auto timerHighResClock() {
  return std::chrono::high_resolution_clock::now();
}

[[maybe_unused]] inline auto timerRdtscp() {
  unsigned int auxInfo{};
  return __rdtscp(&auxInfo);
}

// Current Timer
inline auto timer() {
  return timerSteadyClock();
}

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
