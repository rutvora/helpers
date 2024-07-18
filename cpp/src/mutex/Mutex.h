//
// Created by rutvora on 7/17/24.
//

#ifndef INTERCONNECT_SIDE_CHANNELS_SUBMODULES_HELPERS_CPP_SRC_MUTEX_MUTEX_H_
#define INTERCONNECT_SIDE_CHANNELS_SUBMODULES_HELPERS_CPP_SRC_MUTEX_MUTEX_H_

// A mutex class satisfying TimedLockable requirements
class Mutex {
 public:
  void lock();
  void unlock();
  bool try_lock();
  template<typename Rep, typename Period>
  bool try_lock_for(const std::chrono::duration<Rep, Period> &timeToWaitFor);
  template<typename Clock, typename Duration>
  bool try_lock_until(const std::chrono::time_point<Clock, Duration> &timeToWaitUntil);
 private:
  std::atomic_flag busy = false;
};

#include "Mutex.tpp"

#endif //INTERCONNECT_SIDE_CHANNELS_SUBMODULES_HELPERS_CPP_SRC_MUTEX_MUTEX_H_
