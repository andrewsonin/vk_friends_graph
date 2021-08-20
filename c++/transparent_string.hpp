#ifndef TRANSPARENT_STRING_HPP
#define TRANSPARENT_STRING_HPP

#include <unordered_map>
#include <unordered_set>

namespace HashContainerUtils::String {
    class Transparent {
    public:
        Transparent(std::string_view &&string) : PossibleString(nullptr), data(string) {}

        Transparent(const std::string_view &string) : PossibleString(nullptr), data(string) {}

        Transparent(std::string &&string) : PossibleString(new std::string(std::forward<std::string>(string))),
                                            data(*PossibleString) {}

        Transparent(const std::string &string) : PossibleString(new std::string(string)), data(*PossibleString) {}

        Transparent(const char *string) : PossibleString(new std::string(string)), data(*PossibleString) {}

        bool operator==(const Transparent &other) const {
            return data == other.data;
        }

        ~Transparent() {
            delete PossibleString;
        }

        [[nodiscard]] std::pair<std::string_view, bool> getString() const noexcept {
            // Returns a pair of stored std::string_view and a boolean indicating whether std::string was stored
            return std::make_pair(data, PossibleString);
        }

        friend struct Hash;

    private:
        std::string *PossibleString;
        std::string_view data;
    };

    struct Hash {
        auto operator()(const Transparent &string) const {
            return std::hash<std::string_view>()(string.data);
        }
    };

    template<typename V>
    using Map = std::unordered_map<Transparent, V, Hash>;

    using Set = std::unordered_set<Transparent, Hash>;
}

#endif // TRANSPARENT_STRING_HPP