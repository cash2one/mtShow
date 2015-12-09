all:jxdecode.so
	rm -rf jxencryption.o src4py.o
	rm -rf cass_pack_factory_src.o cass_pack_Factorysrc4py.o

jxdecode.so:jxencryption.o src4py.o
	g++ src4py.o -o jxdecode.so -shared -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ -L/usr/local/lib/python2.7/ -L/usr/local/lib/ -lboost_python -lssl
jxencryption.o:
	g++ -c jxencryption.cpp -o jxencryption.o -lcrypto 
src4py.o:jxencryption.o
	g++ -c src4py.cpp -o src4py.o -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ 

clean:
	rm -rf jxencryption.o src4py.o
	rm -rf jxdecode.so 



