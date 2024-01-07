//
// Created by rutvora on 12/22/23.
//

#ifndef HELPERS_PRINTERS_H_
#define HELPERS_PRINTERS_H_

#include <iostream>
#include <vector>

// Print a variable, while accounting for the following type exceptions:
// 1. uint8_t is printed as an integer, not a character
template<typename Type>
inline void printValue(std::ostream &os, const Type &value);

// Print an std::vector
template<typename Type>
inline std::ostream &operator<<(std::ostream &os, const std::vector<Type> &vec) {
  os << "[";
  if (vec.empty()) {
    os << "]";
    return os;
  }
  for (const Type &entry : vec) {
    printValue(os, entry);
    os << ", ";
  }
  os << '\b' << '\b' << "]";
  return os;
}

// Print an std::unordered_map
template<typename Key, typename Tp>
inline std::ostream &operator<<(std::ostream &os, const std::unordered_map<Key, Tp> &map) {
  os << "{";
  if (map.empty()) {
    os << "}";
    return os;
  }
  for (auto [key, value] : map) {
    os << "\"";
    printValue(os, key);
    os << "\": ";
    printValue(os, value);
    os << ", ";
  }
  os << '\b' << '\b' << "}";
  return os;
}

// Print an std::map
template<typename Key, typename Tp>
inline std::ostream &operator<<(std::ostream &os, const std::map<Key, Tp> &map) {
  os << "{";
  if (map.empty()) {
    os << "}";
    return os;
  }
  for (auto [key, value] : map) {
    os << "\"";
    printValue(os, key);
    os << "\": ";
    printValue(os, value);
    os << ", ";
  }
  os << '\b' << '\b' << "}";
  return os;
}

// Print a variable, while accounting for the following type exceptions:
// 1. uint8_t is printed as an integer, not a character
template<typename Type>
inline void printValue(std::ostream &os, const Type &value) {
  if constexpr (std::is_same<Type, uint8_t>::value) {
    os << static_cast<int>(value);
  } else {
    os << value;
  }
}

#endif //HELPERS_PRINTERS_H_
