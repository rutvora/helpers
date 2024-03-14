//
// Created by rutvora on 10/31/23.
//

[[maybe_unused]] [[gnu::always_inline]] [[clang::always_inline]]
static inline uint64_t getDiff(uint64_t start, uint64_t end) {
  return end - start;
}

[[maybe_unused]] [[gnu::always_inline]] [[clang::always_inline]]
static inline uint64_t getDiff(std::chrono::time_point<std::chrono::steady_clock> &start,
                               std::chrono::time_point<std::chrono::steady_clock> &end) {
  return (end - start).count();
}

[[maybe_unused]] [[gnu::always_inline]] [[clang::always_inline]]
static inline uint64_t getDiff(std::chrono::time_point<std::chrono::high_resolution_clock> &start,
                               std::chrono::time_point<std::chrono::high_resolution_clock> &end) {
  return (end - start).count();
}

template<typename ReturnType, typename Func, typename... Args>
requires Profile::validFunctionWithRet<ReturnType, Func, Args...>
std::pair<uint64_t, ReturnType> Profile::profile(const Func &function, Args &... args) {
#if TIMER_FENCE == TIMER_FEATURE_ON
  TIMER_FENCE_TYPE();
#endif

  auto start = PROFILE_TIMER();
  auto output = function(args...);

#if TIMER_FENCE == TIMER_FEATURE_ON
  TIMER_FENCE_TYPE();
#endif
  auto end = PROFILE_TIMER();

  return {getDiff(start, end), output};
}

template<typename Func, typename... Args>
requires Profile::validFunctionWithoutRet<Func, Args...>
uint64_t Profile::profile(const Func &function, Args &... args) {
#if TIMER_FENCE == TIMER_FEATURE_ON
  TIMER_FENCE_TYPE();
#endif

  auto start = PROFILE_TIMER();
  function(args...);

#if TIMER_FENCE == TIMER_FEATURE_ON
  TIMER_FENCE_TYPE();
#endif
  auto end = PROFILE_TIMER();

  return getDiff(start, end);
}