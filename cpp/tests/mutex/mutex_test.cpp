//
// Created by rutvora on 7/17/24.
//

#include <cassert>
#include <thread>
#include "Mutex.h"

int main() {
  Mutex mutex{};
  assert(mutex.try_lock()); // See if you can lock the mutex that was just initialized
  assert(!mutex.try_lock()); // Try to lock the mutex again, should fail
  mutex.unlock(); // Unlock the mutex
  assert(mutex.try_lock()); // Try to lock the mutex again, should succeed

  auto now = std::chrono::steady_clock::now();
  assert(!mutex.try_lock_for(std::chrono::seconds(1))); // Should not lock, and should time out
  assert(std::chrono::steady_clock::now() > now + std::chrono::seconds(1)); // Make sure it actually timed out
  mutex.unlock();
  now = std::chrono::steady_clock::now();
  assert(mutex.try_lock_for(std::chrono::seconds(1))); // Should lock, and should not time out
  assert(std::chrono::steady_clock::now() < now + std::chrono::seconds(1)); // Make sure it did not time out

  now = std::chrono::steady_clock::now();
  assert(!mutex.try_lock_until(now + std::chrono::seconds(1))); // Should not lock, and should time out
  assert(std::chrono::steady_clock::now() > now + std::chrono::seconds(1)); // Make sure it actually timed out
  mutex.unlock();
  now = std::chrono::steady_clock::now();
  assert(mutex.try_lock_until(now + std::chrono::seconds(1))); // Should lock, and should not time out
  assert(std::chrono::steady_clock::now() < now + std::chrono::seconds(1)); // Make sure it did not time out
  return 0;
}