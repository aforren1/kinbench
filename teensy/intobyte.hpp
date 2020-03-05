#include <cstring>
#include <iterator>

template <typename Iterator, typename T>
static void intoByte(Iterator &it, const T val)
{
    memcpy(it, &val, sizeof(T));
    it += sizeof(T);
}

template <typename Iterator, typename T, typename... Args>
static void intoByte(Iterator &it, const T val, Args... Fargs)
{
    intoByte(it, val);
    intoByte(it, Fargs...);
}
