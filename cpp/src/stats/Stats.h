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
#include <utility>
#include <set>

template<typename T>
concept Number = std::is_arithmetic_v<T>;

template<Number T>
class Stats {
 public:
  struct Value {
    T val;
    uint64_t timeStamp;
    Value(T value, uint64_t timeStamp) : val(value), timeStamp(timeStamp) {}
    bool operator<(const Value &rhs) const {
      return val < rhs.val;
    }
  };

  std::atomic<double> avg{0}, stdev{0};
  std::atomic<T> min{std::numeric_limits<T>::max()}, max{std::numeric_limits<T>::lowest()};
  /**
 * Function to write the relevant variables of this class to a json object
 * @param j The json object to write
 * @param stats The instance of the stats class to get the values from
 */
  [[maybe_unused]]
  friend void to_json(nlohmann::ordered_json &j, const Stats<T> &stats) {
    // Calculate the median
    double median = nanf64("Store vals is false");
    if (stats.storeVals && stats.values.size() > 0) {
      // Update Median
      auto middleElem = std::next(stats.values.begin(), stats.values.size() / 2);
      if (stats.values.size() % 2 == 0) {
        median = ((*middleElem).val + (*std::prev(middleElem)).val) / 2;
      } else {
        median = (*middleElem).val;
      }
    }
    j = {
        {"unit", stats.unit},
        {"avg", stats.avg.load()},
        {"stdev", stats.stdev.load()},
        {"median", median},
        {"min", stats.min.load()},
        {"minIdx", stats.minIdx.load()},
        {"max", stats.max.load()},
        {"maxIdx", stats.maxIdx.load()},
        {"count", stats.count.load()},
        {"values", stats.values},
    };
  };
  [[maybe_unused]]
  friend void to_json(nlohmann::json &j, const Stats<T> &stats) {

    // Calculate the median
    double median = nanf64("Store vals is false");
    if (stats.storeVals && stats.values.size() > 0) {
      // Update Median
      auto middleElem = std::next(stats.values.begin(), stats.values.size() / 2);
      if (stats.values.size() % 2 == 0) {
        median = ((*middleElem).val + (*std::prev(middleElem)).val) / 2;
      } else {
        median = (*middleElem).val;
      }
    }
    j = {
        {"unit", stats.unit},
        {"avg", stats.avg.load()},
        {"stdev", stats.stdev.load()},
        {"median", median},
        {"min", stats.min.load()},
        {"minIdx", stats.minIdx.load()},
        {"max", stats.max.load()},
        {"maxIdx", stats.maxIdx.load()},
        {"count", stats.count.load()},
        {"values", stats.values},
    };
  };

  friend void to_json(nlohmann::json &j, const Stats<T>::Value &value) {
    j = {
        {"value", value.val},
        {"timeStamp", value.timeStamp},
    };
  };

  friend void to_json(nlohmann::ordered_json &j, const Stats<T>::Value &value) {
    j = {
        {"value", value.val},
        {"timeStamp", value.timeStamp},
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
   */
  explicit Stats(std::string unit, const uint64_t ignoreInitial = 0, const bool storeVals = false)
      : unit(std::move(unit)), ignoreInitial(ignoreInitial), ignoreRemaining(ignoreInitial), storeVals(storeVals) {
  }

  /**
   * Update the statistics by adding this new value
   * @param val The new value to incorporate in the statistics
   */
  void update(T val, uint64_t timeStamp = 0);
  /**
   * Update the statistics by adding these new vals
   * @param vals The vals to incorporate in the statistics
   */
  [[maybe_unused]] [[gnu::always_inline]]
  inline void update(const std::vector<T> &vals) {
    for (auto val : vals) {
      update(val);
    }
  }

  /**
 * Update the statistics by adding these new vals
 * @param vals The vals with timestamps to incorporate in the statistics
 */
  [[maybe_unused]] [[gnu::always_inline]]
  inline void update(const std::vector<Value> &vals) {
    for (auto value : vals) {
      update(value.val, value.timeStamp);
    }
  }

  /**
   * Update the statistics by adding these new vals
   * @param vals The vals to incorporate in the statistics
   */
  template<size_t N>
  [[maybe_unused]] [[gnu::always_inline]]
  inline void update(const std::array<T, N> &vals) {
    for (auto val : vals) {
      update(val);
    }
  }

  /**
 * Update the statistics by adding these new vals
 * @param vals The vals with timestamps to incorporate in the statistics
 */
  template<size_t N>
  [[maybe_unused]] [[gnu::always_inline]]
  inline void update(const std::array<Value, N> &vals) {
    for (auto value : vals) {
      update(value.val, value.timeStamp);
    }
  }

  /**
   * Update the statistics by adding these new vals
   * @param vals The vals to incorporate in the statistics
   * @param length The number of values to incorporate
   */
  [[maybe_unused]] [[gnu::always_inline]]
  inline void update(const T *vals, const size_t length) {
    for (size_t i = 0; i < length; i++) {
      update(vals[i]);
    }
  }

  /**
 * Update the statistics by adding these new vals
 * @param vals The vals to incorporate in the statistics
 * @param length The number of values to incorporate
 */
  [[maybe_unused]] [[gnu::always_inline]]
  inline void update(const Value *vals, const size_t length) {
    for (size_t i = 0; i < length; i++) {
      update(vals[i].val, vals[i].timeStamp);
    }
  }

  inline void clear() {
    avg = stdev = M2 = 0;
    min = std::numeric_limits<T>::max();
    max = std::numeric_limits<T>::lowest();
    minIdx = maxIdx = count = 0;
    ignoreRemaining = ignoreInitial;
    values.clear();
  }

 private:
  std::multiset<Value> values{};

  std::atomic<double> M2{0};
  std::atomic<uint64_t> minIdx{0}, maxIdx{0}, count{0};
  std::string unit;
  uint64_t ignoreInitial{0};
  uint64_t ignoreRemaining{0};
  bool storeVals{false};
  std::chrono::time_point<std::chrono::steady_clock> startTime = std::chrono::steady_clock::now();
};

#include "Stats.tpp"

#endif //HELPERS_STATS_H_
