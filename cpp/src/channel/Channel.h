//
// Created by rutvora on 12/11/23.
//

#ifndef HELPERS_CHANNEL_H_
#define HELPERS_CHANNEL_H_

#include <queue>
#include "../mutex/Mutex.h"
#include <condition_variable>

template<typename T, size_t maxSize = 0>
class Channel {
 public:
  Channel() = default;
  virtual ~Channel() = default;
  Channel &operator=(const Channel &other) = delete;
  Channel(const Channel &other) = delete;

  Channel<T, maxSize> &operator<<(const T &data);
  Channel<T, maxSize> &operator>>(T &data);

 private:
  std::queue<T> queue;
  Mutex mutex;
  std::condition_variable_any notEmpty;
  std::condition_variable_any notFull;

  void send(const T &data);
  T &receive();

};
#include "Channel.tpp"
#endif //HELPERS_CHANNEL_H_
