//
// Created by Rut Vora
//

#include "Logging.h"

void Logging::log(const LOGLEVEL &level, const std::string &identifier, const std::string &message) {
  if (logLevel >= level) {
    std::scoped_lock<std::mutex> lock(logMutex);
    double currTime = (double) ((std::chrono::steady_clock::now() - startTime).count()) / 1e9;
    *output << "[" << currTime << "s : " << getLevelString(level) << "]" << " " << identifier << ": " << message
              << std::endl;
  }
}
