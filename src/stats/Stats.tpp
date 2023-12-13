//
// Created by Rut Vora
//

#include <complex>
#include "Stats.h"

template<Number T>
void Stats<T>::update(const T val) {
  if (ignoreRemaining > 0) {
    --ignoreRemaining;
    return;
  }
  if (storeVals) {
    timeStamps.emplace_back((std::chrono::steady_clock::now() - startTime).count());
    values.emplace_back(val);
  }
  if (min > val) {
    min = val;
    minIdx = count.load();
  }
  if (max < val) {
    max = val;
    maxIdx = count.load();
  }
  double delta = (double) val - avg;
  {
    // Calculate mean
    avg =
        (((avg) * (double) count) + (double) val) /
            (double) (count + 1);
  }
  // Calculate variance
  M2.store(M2.load() + delta * ((double) val - avg));
  stdev = sqrt(M2 / (double) (count + 1));
  count++;
}