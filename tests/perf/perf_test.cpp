//
// Created by rutvora on 4/18/24.
//

#include <cassert>
#include "Perf.h"



int main() {

  auto perf = Perf<PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, true, -1>::getInstance();
  assert(perf != nullptr);
  perf->reset();
  perf->enable();

  auto start = perf->readCounter();
  {
    int j = 0;
    for (int i = 0; i < 1000000; i++) {
      j++;
    }
  }
  auto end = perf->readCounter();
  perf->disable();

  assert(end > start);
}
