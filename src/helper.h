//
// Created by rutvora on 11/1/23.
//

// Include all files
#include "Channel.h"
#include "CPU.h"
#include "Logging.h"
#include "Profile.h"
#include "Stats.h"

#ifndef HELPERS_GLOBAL_H_
#define HELPERS_GLOBAL_H_

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

#endif //HELPERS_GLOBAL_H_
