//
// Created by rutvora on 11/1/23.
//

#ifndef INTERCONNECT_SIDE_CHANNELS_HELPERS_CPU_H_
#define INTERCONNECT_SIDE_CHANNELS_HELPERS_CPU_H_

#include <vector>
#include <cstdint>

namespace CPU {
/**
 * Set the CPU affinity to the specified processors
 * @param cpus The list of processors to set the CPU affinity to
 * @return Whether setting the CPU affinity was successful
 */
bool setCPUAffinity(std::vector<uint8_t> &cpus);

/**
 * Move the process to the CSet Shield set up (Refer to main README for more details)
 */
void moveToCSetShield();
}

#endif //INTERCONNECT_SIDE_CHANNELS_HELPERS_CPU_H_
