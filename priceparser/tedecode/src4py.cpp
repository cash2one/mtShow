#include <boost/python.hpp>
#include "src.cpp"
using namespace boost::python;
BOOST_PYTHON_MODULE(tedecode)  //test是python中模块名字
{
        def("tedecode", TeDecode);//将testA映射为a 函数
}
