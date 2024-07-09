//
// Created by rutvora on 10/30/23.
//

#ifndef HELPERS_CONFIG_H
#define HELPERS_CONFIG_H

#include <nlohmann/json.hpp>
#include "log/Logging.h"

NLOHMANN_JSON_SERIALIZE_ENUM(Logging::LOGLEVEL, {
  { Logging::DEBUG, "DEBUG" },
  { Logging::WARN, "WARN" },
  { Logging::ERROR, "ERROR" },
})

using json = nlohmann::json;

/**
 * Configuration for running all experiments
 */
namespace Config {

/**
 * @struct Config
 * @brief The configuration for all experiments
 * @var Config::logLevel
 * The level of logging required (DEBUG, WARN, ERROR)
 * @var Config::resultsFile
 * The file to place the results in
 * @var Config::isolatedCores
 * The list of cores that are isolated using `isolcpus`
 */
struct Config {
  Logging::LOGLEVEL logLevel{Logging::WARN};
  std::string resultsFile{};
  std::vector<uint8_t> isolatedCores{};
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE_WITH_DEFAULT(Config, logLevel, resultsFile, isolatedCores)
}
#endif //HELPERS_CONFIG_H
