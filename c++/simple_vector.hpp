#ifndef VK_SIMPLE_VECTOR_HPP
#define VK_SIMPLE_VECTOR_HPP

#include <cstddef>

template<typename T>
class simple_vector {
public:
    explicit simple_vector(size_t size) : data(new T[size]) {}

    ~simple_vector() {
        delete[] data;
    }

    T *data;
};

#endif // VK_SIMPLE_VECTOR_HPP
