#include <boost/python.hpp>
#include "src.cpp"
using namespace boost::python;
BOOST_PYTHON_MODULE(amdecode)  //test是python中模块名字
{
        def("B64decode", B64Decode);//将testA映射为a 函数
        def("Decrypt", DecryptWinningPrice);//将testA映射为a 函数
        def("decode", TestWinningPrice);//将testA映射为a 函数
}
