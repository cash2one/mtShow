#include <boost/python.hpp>
#include "jxencryption.cpp"
using namespace boost::python;
BOOST_PYTHON_MODULE(jxdecode)  //test是python中模块名字
{
        def("jxdecode", jxdecode);//将testA映射为a 函数
}
