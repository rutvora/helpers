//
// Created by rutvora on 11/1/23.
//

#include <sstream>
#include "include.h"

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
    strStream << "Could not set CPU affinity to " << cpus << " (Error: " << strerror(errno) << ")";
    if (logging != nullptr) {
      logging->log(Logging::ERROR, strStream.str());
    }
    else std::cerr << strStream.str() << std::endl;
    return false;
  }
  return true;
}

void moveToCSetShield() {
  // Move this process inside the shielded group of cores
  std::stringstream command;
  command << "cset shield --shield --pid " << getpid() << " 2>&1";
  std::string cmd = command.str();
  auto out = Sys::run(cmd);
  if (out.contains("tasks are not movable, impossible to move")) {
    if (logging != nullptr)
      logging->log(Logging::ERROR, "Could not move process to shielded group of cores");
    else
      std::cerr << "Could not move process to shielded group of cores" << std::endl;
  }
}
}