#include <iostream>
#include <fstream>
#include <chrono>
#include <thread>

#include "Eigen/Dense"
#include "Eigen/Eigenvalues"
#include "json.hpp"

#include "web_crawler.hpp"
#include "simple_vector.hpp"
#include "graph.hpp"
#include "profiler.hpp"
#include "cmd_parser.hpp"

using Matrix = Eigen::MatrixXd;

const auto HOST = "https://api.vk.com/method/", VERSION = "5.92";

size_t writeFunction(void *, unsigned, unsigned, std::string *);

void build_graph(Graph &graph, const std::string &url_template, std::string &response, unsigned user_VKId,
                 unsigned depth, CURL *curl);

int main(int argc, char *argv[]) {
    /*
     * Build graph of relationships between users of VK social net (https://vk.com), taking the entered user ID as the
     * starting vertex. The graph is build by BFS, only to a certain depth specified by user. At the last recursion
     * step, the edges are added only to the visited vertices.
     *
     * For the constructed graph, a special matrix, called the Laplacian, is created. It is used further for spectral
     * clustering ("A tutorial on spectral clustering" (2007), Ulrike von Luxburg) needed to determine the number of
     * user groups. Spectral clustering considered here is based on the calculation of singular values of the graph
     * Laplacian.
     *
     * Parameters such as STARTING USER ID and DEPTH OF SEARCH are passed as the command line parameters.
     * 1) STARTING USER ID                 [positive integer]
     * 2) DEPTH OF SEARCH                  [positive integer]
     * 3) NAME OF OUT FILE with LAPLACIAN  [String: doesn't save if "n"]
     * 4) NAME OF OUT FILE with EIGENVALS  [String: doesn't save if "n"]
     * 5) ACCESS TOKEN                     [String]
     * 6) DELETE INITIAL USER              [String: "t" is true, else is false]
     */

    CMDParser(argc, argv, {"3", "211"});
    if (argc != 7) {
        std::cerr << "Unexpected number of parameters: " << argc << ", but should be 6.\nPlease, check your input.\n";
        return 1;
    }
    const unsigned UserID = std::stoul(argv[1]), depth = std::stoul(argv[2]);
    const char *const NameOfOutLapl = argv[3], *const NameOfOutEigen = argv[4], *const TOKEN = argv[5];
    const bool DelInitUser = strncmp(argv[6], "t", 2) == 0;

    //------------------------------------------------------------------------------------------------------------------
    //                                       RELATIONSHIP GRAPH BUILDING                                               |
    //------------------------------------------------------------------------------------------------------------------

    Graph graph;
    {
        WebCrawler curl;
        if (!curl) {
            std::cerr << "Curl initialization failure.\nPlease, check your internet connection.\n";
            return 2;
        }

        std::string response;
        const std::string URL_template = [&TOKEN]() {
            std::stringstream URL_template;
            URL_template << HOST << "friends.get?v=" << VERSION << "&access_token=" << TOKEN << "&user_id=";
            return URL_template.str();
        }();

        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeFunction);

        // Graph of VK user relationships
        build_graph(graph, URL_template, response, UserID, depth, curl);
    }

    if (DelInitUser) {
        graph.erase(UserID);
    }

    auto &data = graph.GetData();
    auto &index = graph.GetIndex();
    const auto PeopleNum = index.size();

    //------------------------------------------------------------------------------------------------------------------
    //                                       GRAPH LAPLACIAN COMPUTATION                                               |
    //------------------------------------------------------------------------------------------------------------------
    // Laplacian of the given graph is defined as a matrix equals to the result of subtraction of G from D, where D is
    // a diagonal matrix that stores information about degrees of the vertices, and G is adjacency matrix.
    // The following code block is the computation of this Laplacian.

    Matrix Laplacian(PeopleNum, PeopleNum);
    Laplacian.setZero();

    // Construction of graph Laplacian

    {
        LOG_DURATION("General Laplacian Initialization")
        const unsigned IdxOffset = DelInitUser;
        const auto IndexEnd = index.end();
        for (const auto &[_idx, VKId_and_Friends]: data) {
            const auto idx = _idx - IdxOffset;
            auto column = Laplacian.col(idx);
            for (const auto &friendVKId: VKId_and_Friends.second) {
                const auto friendIdxIt = index.find(friendVKId);
                if (friendIdxIt != IndexEnd) {
                    const auto friendIdx = friendIdxIt->second - IdxOffset;
                    column(friendIdx) = Laplacian(idx, friendIdx) = -1;
                }
            }
        }
    }

    {
        LOG_DURATION("Diagonal Laplacian Initialization")
        Laplacian.diagonal() = -Laplacian.rowwise().sum();
    }

    // Calculation of eigenvalues of Graph Laplacian. Its matrix is self-adjoint due to its diagonal symmetry, so the
    // calculations can be simplified by using special SelfAdjointEigenSolver.

    Eigen::SelfAdjointEigenSolver<Matrix> EigenSolver;
    {
        LOG_DURATION("Calculation of Eigenvectors")
        EigenSolver.compute(Laplacian);
    }

    static const Eigen::IOFormat TSVFormat(Eigen::StreamPrecision, Eigen::DontAlignCols, "\t", "\n");

    if (strncmp(NameOfOutLapl, "n", 2) != 0) {
        const auto &to_print = Laplacian.format(TSVFormat);
        std::ofstream output(NameOfOutLapl);
        output << to_print;
    }

    if (strncmp(NameOfOutEigen, "n", 2) != 0) {
        const auto &to_print = EigenSolver.eigenvalues().transpose().format(TSVFormat);
        std::ofstream output(NameOfOutEigen);
        output << to_print;
    }

    return 0;
}

size_t writeFunction(void *ptr, unsigned size, unsigned Num_MemBytes, std::string *data) {
    const size_t SizeInBytes = size * Num_MemBytes;
    data->append((char *) ptr, SizeInBytes);
    return SizeInBytes;
}

void build_graph(Graph &graph, const std::string &url_template, std::string &response, const unsigned user_VKId,
                 const unsigned depth, CURL *curl) {

    curl_easy_setopt(curl, CURLOPT_URL, (url_template + std::to_string(user_VKId)).c_str());

    std::optional<VectorOfFriends> friends = [&curl, &response, &graph, &user_VKId, &url_template]() {
        while (true) {
            curl_easy_perform(curl);
            const auto report = nlohmann::json::parse(response);
            response.clear();

            const auto end = report.end();
            if (report.find("error") == end) {
                return std::optional(graph.AddUser(user_VKId, report["response"]["items"].get<::VectorOfFriends>()));
            } else {
                const auto &ErrCode = report["error"]["error_code"];
                constexpr char ErrMsgBegin[] = "A profile with ID=",
                        ErrMsgEnd[] = ", so the list of his/her friends cannot be obtained.";
                switch ((unsigned) ErrCode) {
                    case 6:
                        // To many requests per second
                        std::this_thread::sleep_for(std::chrono::seconds(1));
                        continue;
                    case 30:
                        std::cerr << ErrMsgBegin << user_VKId << " is private" << ErrMsgEnd;
                        break;
                    case 18:
                        std::cerr << ErrMsgBegin << user_VKId << " is deleted" << ErrMsgEnd;
                        break;
                    default:
                        std::cerr << "URL response returned unusual error code: " << ErrCode << ". URL request was: "
                                  << url_template << user_VKId;
                }
                std::cerr << std::endl;
                return std::optional<VectorOfFriends>();
            }
        }
    }();

    if (!friends || depth == 0) {
        return;
    }

    auto current_depth = depth - 1;
    for (const auto &VKId: *friends) {
        if (!graph.HasVKId(VKId)) {
            build_graph(graph, url_template, response, VKId, current_depth, curl);
        }
    }
}