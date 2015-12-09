#include <boost/python.hpp>
#include "priceDecrypt.cpp"
using namespace boost::python;
BOOST_PYTHON_MODULE(shdecode)  //test是python中模块名字
{
        def("Hex2String", Hex2String);//将testA(后者)映射为a（前者） 函数
        def("Decrypt", Decrypt);//将testA（后者）映射为a（前者） 函数
        //def("Encrypt", Encrypt);//将testA（后者）映射为a（前者） 函数
}
