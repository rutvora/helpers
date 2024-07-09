#include <vector>
#include <iostream>
#include "Stats.h"

int main() {
  std::vector<int> vec{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
  std::string unit = "unit";
  Stats<int> stats{unit};
  stats.update(vec);
  double avg = stats.avg;
  double stdev = stats.stdev;
  assert(std::abs(avg - 5.5) < 1e-7);
  assert(std::abs(stdev - 2.8) < 1e-1);
  return 0;
}