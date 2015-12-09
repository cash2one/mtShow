#include <boost/python.hpp>
#include "baiencryption.cpp"
using namespace boost::python;
BOOST_PYTHON_MODULE(baidecode)  //test是python中模块名字
{
        def("baidecode", baidecode);//将testA映射为a 函数
}
