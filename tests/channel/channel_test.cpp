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
    channel << 1;
    channel << 2;
    channel << 3; // This should block as the channel is full
  });

  std::thread receiver([&]() {
    int value;
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