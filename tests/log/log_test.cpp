//
// Created by Rut Vora
//

#include "Logging.h"

int main() {
  Logging log{Logging::WARN};
  log.log(Logging::ERROR, "Error message"); // This should print
  log.log(Logging::DEBUG, "Debug message"); // This should not print
  return 0;
}