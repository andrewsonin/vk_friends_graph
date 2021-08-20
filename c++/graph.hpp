#ifndef VK_GRAPH_HPP
#define VK_GRAPH_HPP

#include <unordered_set>
#include <unordered_map>
#include <map>

using VectorOfFriends = std::vector<unsigned>;

class Graph {
    static unsigned maxIdx;
public:
    VectorOfFriends &AddUser(const unsigned VKid, VectorOfFriends setOfFriends) {
        auto idx = maxIdx++;
        VKidToIdx.emplace(VKid, idx);
        return idxToVKid.emplace(idx, std::make_pair(VKid, std::move(setOfFriends))).first->second.second;
    }

    void erase(const unsigned VKid) {
        const auto dataIt = VKidToIdx.find(VKid);
        const auto idx = dataIt->second;
        VKidToIdx.erase(dataIt);
        idxToVKid.erase(idx);
    }

    auto &GetData() const {
        return idxToVKid;
    }

    auto &GetIndex() const {
        return VKidToIdx;
    }

    bool HasVKId(const unsigned VKId) const {
        return VKidToIdx.find(VKId) != VKidToIdx.end();
    }

private:
    std::unordered_map<unsigned, unsigned> VKidToIdx;
    std::map<unsigned, std::pair<unsigned, VectorOfFriends>> idxToVKid;
};

unsigned Graph::maxIdx = 0;

#endif // VK_GRAPH_HPP
