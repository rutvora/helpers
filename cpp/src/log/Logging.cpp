//
// Created by Rut Vora
//

#include "Logging.h"

void Logging::log(const LOGLEVEL &level,
                  const std::string &message,
                  const std::string& identifier,
                  const std::source_location location) {
  if (logLevel >= level) {
    std::scoped_lock<std::mutex> lock(logMutex);
    double currTime = (double) ((std::chrono::steady_clock::now() - startTime).count()) / 1e9;
    *output << location.file_name() << ":" << location.line() << "\t"
            << "[" << currTime << "s : " << getLevelString(level) << "]"
            << "\t" << identifier << "\t" << message << std::endl;
  }
}
