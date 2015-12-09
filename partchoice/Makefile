all:amdecode.so
	rm -rf src.o src4py.o
	rm -rf cass_pack_factory_src.o cass_pack_Factorysrc4py.o

amdecode.so:src.o src4py.o
	g++ src4py.o -o partchoice.so -shared -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ -L/usr/local/lib/python2.7/ -L/usr/local/lib/ -lboost_python -lssl -lcrypto
src.o:
	g++ -c src.cpp -o src.o 
src4py.o:src.o
	g++ -c src4py.cpp -o src4py.o -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ 

clean:
	rm -rf src.o src4py.o
	rm -rf partchoice.so 
