//
// Created by rutvora on 10/31/23.
//

// Uses stead_clock

template<typename ReturnType, typename Func, typename... Args>
requires Profile::validFunctionWithRet<ReturnType, Func, Args...>
std::pair<uint64_t, ReturnType> Profile::profile(Func &function, Args &... args) {
  auto start = timer();
  auto output = function(args...);
  auto end = timer();
  return {(end - start).count(), output};
}

template<typename Func, typename... Args>
requires Profile::validFunctionWithoutRet<Func, Args...>
uint64_t Profile::profile(Func &function, Args &... args) {
  auto start = timer();
  function(args...);
  auto end = timer();
  return (end - start).count();
}