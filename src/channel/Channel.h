//
// Created by rutvora on 12/11/23.
//

#ifndef INTERCONNECT_SIDE_CHANNELS_SRC_HELPERS_CHANNEL_H_
#define INTERCONNECT_SIDE_CHANNELS_SRC_HELPERS_CHANNEL_H_

#include <queue>
#include <mutex>
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
  std::mutex mutex;
  std::condition_variable notEmpty;
  std::condition_variable notFull;

  void send(T data);
  T receive();

};
#include "Channel.tpp"
#endif //INTERCONNECT_SIDE_CHANNELS_SRC_HELPERS_CHANNEL_H_
