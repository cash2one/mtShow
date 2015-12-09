#include <boost/python.hpp>
#include "decode.cpp"
using namespace boost::python;
BOOST_PYTHON_MODULE(gydecode)  //test是python中模块名字
{
        def("gydecode", gydecode);//将testA映射为a 函数
}
