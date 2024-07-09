# Summary

This repo contains some helper functions and structs to be used in general for system research/analysis. You can include
the relevant headers in your program for use.

Below are the descriptions of the helpers

## Channel

This is a naive implementation of channels from Go. They are used for simple inter-thread communication.
By default, the channels are unlimited in size and the underlying data-structure scales up as need be. You can use any
class or data-type within this channel.

## CPU

This library can be used for running processes in isolated CPU cores:

## Log

This class helps you log the output to the specified file (defaults to stderr)

## Profile

This template allows you to supply any function to profile (get the runtime of)

## Stats

This class instance can be used to record the statistics of any numeric data type. Currently supported statistics are:
Avg, Stdev, Min and Max (and their indices). They also record the total number of inputs, and optionally store all the
inputs. You can also choose to ignore the initial 'n' entries (warm-up phase of your code)

## Sys

This library provides wrappers around the system functionalities. Currently, the following functionalities are
available:

- `std::string run(std::string &cmd, bool stdout, bool stderr)`: Runs the given command as a child process, and returns the selected outputs of
  the command as a string