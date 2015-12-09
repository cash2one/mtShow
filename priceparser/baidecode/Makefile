all:baidecode.so
	rm -rf baiencryption.o src4py.o
	rm -rf cass_pack_factory_src.o cass_pack_Factorysrc4py.o

baidecode.so:baiencryption.o src4py.o
	g++ src4py.o -o baidecode.so -shared -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ -L/usr/local/lib/python2.7/ -L/usr/local/lib/ -lboost_python -lssl
baiencryption.o:
	g++ -c baiencryption.cpp -o baiencryption.o -lcrypto 
src4py.o:baiencryption.o
	g++ -c src4py.cpp -o src4py.o -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ 

clean:
	rm -rf baiencryption.o src4py.o
	rm -rf baidecode.so 



