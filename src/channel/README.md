## Channel

This is a naive implementation of channels from Go. They are used for simple inter-thread communication.
By default, the channels are unlimited in size and the underlying data-structure scales up as need be. You can use any
class or data-type within this channel.

You can optionally limit the maximum size of the channel.

_Note: This data structure is thread-safe and multiple threads can operate on it. However, ordering the access (
read/write) amongst multiple producers/consumers is left to the user_

Usage:

```c++
Channel<int> unlimitedChannel{};  // Grows with more data
Channel<CustomClass, 5> limitedChannel{}; // Maximum 5 units of data allowed
// From thread 1:
int toSend = 100;
unlimitedChannel << toSend;

// From thread 2:
int receive;
unllimitedChannel >> receive;   // This blocks until thread 1 sends some data (i.e. there is data to read)
```