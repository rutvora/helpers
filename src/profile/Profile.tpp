//
// Created by rutvora on 10/31/23.
//

// Uses stead_clock

template<typename ReturnType, typename Func, typename... Args>
requires Profile::validFunctionWithRet<ReturnType, Func, Args...>
std::pair<uint64_t, ReturnType> Profile::profile(const Func &function, Args &... args) {
  auto start = timer();
  auto output = function(args...);
  auto end = timer();
#if PROFILE_TIMER == TIMER_STEADY_CLOCK || PROFILE_TIMER == TIMER_HIGH_RES_CLOCK
  return {(end - start).count(), output};
#else
  return {end - start, output};
#endif
}

template<typename Func, typename... Args>
requires Profile::validFunctionWithoutRet<Func, Args...>
uint64_t Profile::profile(const Func &function, Args &... args) {
  auto start = timer();
  function(args...);
  auto end = timer();
#if PROFILE_TIMER == TIMER_STEADY_CLOCK || PROFILE_TIMER == TIMER_HIGH_RES_CLOCK
  return (end - start).count();
#else
  return end - start;
#endif
}