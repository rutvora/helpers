//
// Created by rutvora on 11/1/23.
//

#include <sstream>
#include "CPU.h"
#include "log/Logging.h"
#include "global.h"

namespace CPU {
bool setCPUAffinity(std::vector<uint8_t> &cpus) {
  if (cpus.empty()) return true;
  cpu_set_t mask;
  CPU_ZERO(&mask);
  for (int cpu : cpus) {
    CPU_SET(cpu, &mask);
  }
  auto result = sched_setaffinity(0, sizeof(mask), &mask);
  if (result == -1) {
    std::stringstream strStream;
    strStream << "Could not set CPU affinity to " << cpus;
    Logging::log(Logging::ERROR, "CPU", strStream.str());
    return false;
  }
  return true;
}

void moveToCSetShield() {
  // Move this process inside the shielded group of cores
  std::stringstream command;
  command << "cset shield --shield --pid " << getpid();
  system(command.str().c_str());
}
}