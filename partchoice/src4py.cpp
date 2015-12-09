#include <boost/python.hpp>
#include "src.cpp"
using namespace boost::python;
BOOST_PYTHON_MODULE(partchoice)  //test是python中模块名字
{
        def("GtAdpLogsMd5", GtAdpLogsMd5);//将testA映射为a 函数
}
