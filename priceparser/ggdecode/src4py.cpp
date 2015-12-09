#include <boost/python.hpp>
#include "decrypter.cc"
using namespace boost::python;
BOOST_PYTHON_MODULE(ggdecode)  //test是python中模块名字
{
        def("ggdecode", ggdecode);//将testA映射为a 函数
}
