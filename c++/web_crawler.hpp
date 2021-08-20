#ifndef VK_WEB_CRAWLER_HPP
#define VK_WEB_CRAWLER_HPP

#include <curl/curl.h>

class WebCrawler {
public:
    WebCrawler() : curl(curl_easy_init()) {}

    ~WebCrawler() {
        curl_easy_cleanup(curl);
    }

    CURL *operator*() const {
        return curl;
    }

    explicit operator bool() const {
        return curl;
    }

    operator CURL *() const {
        return curl;
    }

private:
    CURL *curl;
};

#endif // VK_WEB_CRAWLER_HPP
