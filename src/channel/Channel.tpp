//
// Created by rutvora on 12/11/23.
//


template<typename T, size_t maxSize>
void Channel<T, maxSize>::send(T data) {
  std::unique_lock<std::mutex> lock(mutex);
  if (maxSize > 0) {
    while (queue.size() >= maxSize) {
      notFull.wait(lock);
    }
  }
  queue.push(data);
  notEmpty.notify_one();
}

template<typename T, size_t maxSize>
T Channel<T, maxSize>::receive() {
  std::unique_lock<std::mutex> lock(mutex);
  while (queue.empty()) {
    notEmpty.wait(lock);
  }
  T data = queue.front();
  queue.pop();
  notFull.notify_one();
  return data;
}

template<typename T, size_t maxSize>
Channel<T, maxSize> &Channel<T, maxSize>::operator<<(const T &data) {
  send(data);
  return *this;
}

template<typename T, size_t maxSize>
Channel<T, maxSize> &Channel<T, maxSize>::operator>>(T &data) {
  data = receive();
  return *this;
}