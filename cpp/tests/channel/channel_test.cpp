//
// Created by Rut Vora
//

#include <thread>
#include <chrono>
#include <cassert>
#include "Channel.h"

void testChannelBasic() {
  Channel<int> channel;
  int sentValue = 42;
  int receivedValue;

  std::thread sender([&]() {
    channel << sentValue;
  });

  std::thread receiver([&]() {
    std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Allow time for sender to execute
    channel >> receivedValue;
  });

  sender.join();
  receiver.join();

  assert(sentValue == receivedValue);
}

void testChannelBlocking() {
  const size_t MaxSize = 2;
  Channel<int, MaxSize> channel;

  std::thread sender([&]() {
    auto start = std::chrono::steady_clock::now();
    channel << 1;
    assert(std::chrono::steady_clock::now() < start + std::chrono::seconds(1)); // Should not block
    start = std::chrono::steady_clock::now();
    channel << 2;
    assert(std::chrono::steady_clock::now() < start + std::chrono::seconds(1)); // Should not block
    start = std::chrono::steady_clock::now();
    channel << 3; // This should block as the channel is full
    assert(std::chrono::steady_clock::now() > start + std::chrono::seconds(1)); // Should block
  });

  std::thread receiver([&]() {
    int value;
    std::this_thread::sleep_for(std::chrono::seconds(1)); // Sender should block on the third insertion
    channel >> value;
    assert(value == 1);

    channel >> value;
    assert(value == 2);

    // The sender has added more items to the channel, and this should unblock the sender
    channel >> value;
    assert(value == 3);
  });

  sender.join();
  receiver.join();
}

int main() {
  testChannelBasic();
  testChannelBlocking();
  return 0;
}