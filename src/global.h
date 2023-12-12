//
// Created by rutvora on 11/1/23.
//

#ifndef INTERCONNECT_SIDE_CHANNELS_HELPERS_GLOBAL_H_
#define INTERCONNECT_SIDE_CHANNELS_HELPERS_GLOBAL_H_

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

#endif //INTERCONNECT_SIDE_CHANNELS_HELPERS_GLOBAL_H_
