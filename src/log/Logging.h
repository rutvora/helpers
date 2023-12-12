//
// Created by Rut Vora
//

#ifndef HELPERS_LOGGING_H_
#define HELPERS_LOGGING_H_

#include <mutex>
#include <string>
#include <iostream>
#include <chrono>
#include <nlohmann/json.hpp>
#include <fstream>


class Logging {
 public:
/**
 * The values are same as the LOG_LEVEL_XXXX in the main CMakeLists.txt
 * This enum is used mainly for to/from JSON
 */
  enum LOGLEVEL {
    ERROR, WARN, DEBUG
  };

  NLOHMANN_JSON_SERIALIZE_ENUM(Logging::LOGLEVEL, {
    { Logging::DEBUG, "DEBUG" },
    { Logging::WARN, "WARN" },
    { Logging::ERROR, "ERROR" },
  })

  explicit Logging(LOGLEVEL logLevel, const std::string& outputFile = "") : logLevel(logLevel) {
    if (!outputFile.empty()) {
      std::ofstream output(outputFile);
      this->output = &output;
    }
  }

  /**
 * Log the given message
 * @param level The log level
 * @param identifier The invoker (who invokes this log function)
 * @param message The message to be logged
 */
  void log(LOGLEVEL level, const std::string &identifier, const std::string &message);

 private:
  LOGLEVEL logLevel;
  std::ostream *output{&std::cerr};
  std::chrono::time_point<std::chrono::steady_clock> startTime =
      std::chrono::steady_clock::now();  // Start Time of the program
  std::mutex logMutex;  // Mutex for logging

  /**
 * Get the string of the log level to print out to the log
 * @param level The log level to get the string of
 * @return The string corresponding to the log level
 */
  static inline std::string getLevelString(LOGLEVEL level) {
    switch (level) {
      case LOG_LEVEL_ERROR:return "ERROR";
      case LOG_LEVEL_WARN:return "WARNING";
      case LOG_LEVEL_DEBUG:return "DEBUG";
    }
    return "Unknown";
  }
};

#endif //HELPERS_LOGGING_H_
