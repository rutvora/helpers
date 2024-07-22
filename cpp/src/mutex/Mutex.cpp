//
// Created by rutvora on 7/22/24.
//

#include "Mutex.h"

void Mutex::lock() {
  while (busy.test_and_set());
}
void Mutex::unlock() {
  busy.clear();
}
bool Mutex::try_lock() {
  return !busy.test_and_set();
}