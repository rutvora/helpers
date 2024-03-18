//
// Created by rutvora on 3/18/24.
//

#include "Sys.h"
#include "include.h"
#include "cstdio"

extern Logging *logging;  // Defined in main.cu

std::string Sys::run(std::string &cmd, bool stdout, bool stderr) {
    std::string redirection;
    if (stdout && stderr) {
        redirection = " 2>&1";
    } else if (stdout && !stderr) {
        redirection = " 2>/dev/null";
    } else if (!stdout && stderr) {
        redirection = " 2>&1 >/dev/null";
    } else if (!stdout && !stderr) {
        redirection = " >/dev/null 2>&1";
    }
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen((cmd + redirection).c_str(), "r"), &pclose);

    if (!pipe) {
        std::stringstream strStream;
        strStream << "Error running command" << cmd << ":\t" << strerror(errno);
        if (logging != nullptr) {
            logging->log(Logging::ERROR, strStream.str());
        } else {
            std::cerr << strStream.str() << std::endl;
        }
        return "";
    }
    std::array<char, 4096> buffer{};
    std::string out;
    // Read stdout
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
         out += buffer.data();
    }

    return out;
}