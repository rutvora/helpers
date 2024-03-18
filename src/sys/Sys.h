//
// Created by rutvora on 3/18/24.
//

#ifndef HELPERS_SYS_H
#define HELPERS_SYS_H

#include <string>

namespace Sys {

    /** Run a command and return the output
     * @param cmd The command to run
     * @return The stdout of the command (use 2>&1 to capture stderr as well)
     */
    std::string run(std::string &cmd, bool stdout = true, bool stderr = false);
}

#endif //HELPERS_SYS_H
