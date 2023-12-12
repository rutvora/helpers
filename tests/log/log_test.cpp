//
// Created by Rut Vora
//

#include "Logging.h"

int main() {
  Logging log{Logging::WARN};
  log.log(Logging::ERROR, "identifier", "Error message"); // This should print
  log.log(Logging::DEBUG, "identifier", "Debug message"); // This should not print
  return 0;
}