//
// Created by Rut Vora
//

#ifndef HELPERS_STATS_H_
#define HELPERS_STATS_H_

#include <cstdint>
#include <nlohmann/json.hpp>
#include <mutex>
#include <atomic>
#include <chrono>

template<typename T>
concept Number = std::is_arithmetic_v<T>;

template<Number T>
class Stats {
 public:
  std::atomic<double> avg{0}, stdev{0}, min{std::numeric_limits<T>::max()}, max{std::numeric_limits<T>::lowest()};
  /**
 * Function to write the relevant variables of this class to a json object
 * @param j The json object to write
 * @param stats The instance of the stats class to get the values from
 */
  [[maybe_unused]]
  friend void to_json(nlohmann::ordered_json &j, const Stats<T> &stats) {
    j = {
        {"unit", stats.unit},
        {"avg", stats.avg.load()},
        {"stdev", stats.stdev.load()},
        {"min", stats.min.load()},
        {"minIdx", stats.minIdx.load()},
        {"max", stats.max.load()},
        {"maxIdx", stats.maxIdx.load()},
        {"count", stats.count.load()},
        {"values", stats.values},
        {"timeStamps", stats.timeStamps}
    };
  };
  [[maybe_unused]]
  friend void to_json(nlohmann::json &j, const Stats<T> &stats) {
    j = {
        {"unit", stats.unit},
        {"avg", stats.avg.load()},
        {"stdev", stats.stdev.load()},
        {"min", stats.min.load()},
        {"minIdx", stats.minIdx.load()},
        {"max", stats.max.load()},
        {"maxIdx", stats.maxIdx.load()},
        {"count", stats.count.load()},
        {"values", stats.values},
        {"timeStamps", stats.timeStamps}
    };
  };

  // Overload the << operator to print the stats
  friend std::ostream &operator<<(std::ostream &os, const Stats<T> &stats) {
    nlohmann::ordered_json statsJson{stats};
    os << statsJson.dump(2);
    return os;
  };

  /**
   * Constructor
   * @param unit The unit of measurement (appended to the output)
   * @param ignoreInitial The number of initial values to ignore
   * @param storeVals Whether to store the values or not
   * @param expectedEntries Pre-allocate a vector with these many entries to store the values
   */
  explicit Stats(std::string &unit, uint64_t ignoreInitial = 0, bool storeVals = false, uint64_t expectedEntries = 1e3)
      : unit(std::move(unit)), ignoreInitial(ignoreInitial), ignoreRemaining(ignoreInitial), storeVals(storeVals) {
    timeStamps.reserve(expectedEntries);
    if (storeVals) values.reserve(expectedEntries);
  }

  /**
   * Update the statistics by adding this new value
   * @param val The new value to incorporate in the statistics
   */
  void update(T val);

  /**
   * Update the statistics by adding these new vals
   * @param vals The vals to incorporate in the statistics
   */
  [[maybe_unused]]
  inline void update(const std::vector<T> &vals) {
    for (auto val : vals) {
      update(val);
    }
  }

  inline void clear() {
    avg = stdev = M2 = 0;
    min = std::numeric_limits<T>::max();
    max = std::numeric_limits<T>::lowest();
    minIdx = maxIdx = count = 0;
    ignoreRemaining = ignoreInitial;
  }

 private:
  std::atomic<double> M2{0};
  std::atomic<uint64_t> minIdx{0}, maxIdx{0}, count{0};
  std::string unit;
  uint64_t ignoreInitial{0};
  uint64_t ignoreRemaining{0};
  bool storeVals{false};
  std::vector<uint64_t> values{};
  std::chrono::time_point<std::chrono::steady_clock> startTime = std::chrono::steady_clock::now();
  std::vector<uint64_t> timeStamps{};
};

#include "Stats.tpp"

#endif //HELPERS_STATS_H_
