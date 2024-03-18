## Stats

This class instance can be used to record the statistics of any numeric data type. Currently supported statistics are:
Avg, Stdev, Min and Max (and their indices). They also record the total number of inputs, and optionally store all the
inputs. You can also choose to ignore the initial 'n' entries (warm-up phase of your code)

Usage:

```c++
Stats<int> stats{"nanoseconds", 1e2, true, 1e7}; // Unit: "nanoseconds", "ignoreInitial": 100, "storeVals": true, "expectedVals": 1e7
stats.update(5);  // Update with single value
std::vector<int> values{1, 2, 3};
stats.update(values); // Update with multiple values
```