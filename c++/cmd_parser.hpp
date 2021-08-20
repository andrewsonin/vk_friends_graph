#ifndef CMD_PARSER_HPP
#define CMD_PARSER_HPP

#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "transparent_string.hpp"

class CMDParser {

    using SetOfStrings = std::unordered_set<HashContainerUtils::String, HashContainerUtils::Hash>;

public:

    CMDParser(int argc, char **argv) : argc(argc), argv(argv) {
        Parse();
    }

    CMDParser(int argc, char **argv, SetOfStrings allowed_flags) : argc(argc), argv(argv),
                                                                   __allowed_flags(std::move(allowed_flags)) {
        Parse();
    }

private:
    using ValueAndKeyPos = std::pair<std::optional<std::string_view>, int>;
    using NamedValues = std::unordered_map<HashContainerUtils::String, ValueAndKeyPos, HashContainerUtils::Hash>;
    // Is for named values and flags like the following: "--bob <value1> --alice <value2> -g <value3> -p --eve --gregory <value4>"
    // In this case, NamedValues would look like {
    //            "--bob":     {<value1>, 1},
    //            "--alice":   {<value2>, 3},
    //            "-g":        {<value3>, 5},
    //            "-p":        { None,    7},
    //            "--eve":     { None,    8},
    //            "--gregory": {<value4>, 9}
    // }
    using SequentialValues = std::vector<std::pair<HashContainerUtils::String, int>>;
    // The last int in a pair indicates the position
    // Is for sequential unnamed values like the following: "<value5> <value6> <value7>"

    const int argc;
    const char *const *const argv;

    NamedValues params;
    SequentialValues seqValues;

    SetOfStrings __allowed_flags;

    void Parse() {
        std::optional<std::string_view> prevToken;
        for (int i = 1; i != argc; ++i) {
            std::string_view Token(argv[i]);
            if (Token[0] == '-') {
                if (prevToken) {

                }
            } else if (prevToken) {

            } else {
                seqValues.push_back(Token);
            }
        }
    }

};

#endif // CMD_PARSER_HPP
