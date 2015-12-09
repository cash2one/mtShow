all:gydecode.so
	rm -rf decode.o src4py.o
	rm -rf cass_pack_factory_src.o cass_pack_Factorysrc4py.o

gydecode.so:decode.o src4py.o
	g++ src4py.o -o gydecode.so -shared -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ -L/usr/local/lib/python2.7/ -L/usr/local/lib/ -lboost_python -lssl
decode.o:
	g++ -c decode.cpp -o decode.o -lcrypto 
src4py.o:decode.o
	g++ -c src4py.cpp -o src4py.o -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ 

clean:
	rm -rf decode.o src4py.o
	rm -rf gydecode.so 



