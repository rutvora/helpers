//
// Created by rutvora on 11/1/23.
//

#include <sstream>
#include "CPU.h"
#include "log/Logging.h"
#include "helper.h"

extern Logging *logging;  // Defined in main.cu

namespace CPU {
bool setCPUAffinity(const std::vector<uint8_t> &cpus) {
  if (cpus.empty()) return true;
  cpu_set_t mask;
  CPU_ZERO(&mask);
  for (int cpu : cpus) {
    CPU_SET(cpu, &mask);
  }
  auto result = sched_setaffinity(0, sizeof(mask), &mask);
  if (result == -1) {
    std::stringstream strStream;
    std::cerr << "Could not set CPU affinity to " << cpus;
    return false;
  }
  return true;
}

void moveToCSetShield() {
  // Move this process inside the shielded group of cores
  std::stringstream command;
  command << "cset shield --shield --pid " << getpid() << "> /dev/null 2>&1";
  if (system(command.str().c_str()) != 0) {
    if (logging != nullptr)
      logging->log(Logging::ERROR, "CSet shield", "Could not move process to shielded group of cores");
    else
      std::cerr << "Could not move process to shielded group of cores" << std::endl;
  }
}
}