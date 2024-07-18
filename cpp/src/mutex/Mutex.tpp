//
// Created by rutvora on 7/17/24.
//

void Mutex::lock() {
  while (busy.test_and_set());
}
void Mutex::unlock() {
  busy.clear();
}
bool Mutex::try_lock() {
  return !busy.test_and_set();
}
template<typename Rep, typename Period>
bool Mutex::try_lock_for(const std::chrono::duration<Rep, Period> &timeToWaitFor) {
  return try_lock_until(std::chrono::steady_clock::now() + timeToWaitFor);
}
template<typename Clock, typename Duration>
bool Mutex::try_lock_until(const std::chrono::time_point<Clock, Duration> &timeToWaitUntil) {
  while (busy.test_and_set()) {
    if (std::chrono::steady_clock::now() >= timeToWaitUntil) {
      return false;
    }
  }
  return true;
}
