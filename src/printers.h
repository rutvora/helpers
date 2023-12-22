//
// Created by rutvora on 12/22/23.
//

#ifndef HELPERS_PRINTERS_H_
#define HELPERS_PRINTERS_H_

#include <iostream>
#include <vector>

template<typename Type>
std::ostream &operator<<(std::ostream &os, const std::vector<Type> &vec) {
  os << "[";
  if (vec.empty()) {
    os << "]";
    return os;
  }
  for (Type entry : vec) {
    if (std::is_same<Type, uint8_t>::value) {
      os << (int) entry << ", ";
    } else {
      os << entry << ", ";
    }
  }
  os << '\b' << '\b' << "]";
  return os;
}

#endif //HELPERS_PRINTERS_H_
