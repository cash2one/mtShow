

CC = g++
GT_OBJS = ./libdecrypt.a

all: test tedecode.so

test: main.cpp
	$(CC) main.cpp  $(GT_OBJS) -o test

tedecode.so:src.o src4py.o
	$(CC) src4py.o -o tedecode.so $(GT_OBJS) -shared -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ -L/usr/local/lib/python2.7/ -L/usr/local/lib/ -lboost_python -lssl
src.o:
	g++ -c src.cpp $(GT_OBJS) -o src.o 
src4py.o:src.o
	g++ -c src4py.cpp -o src4py.o $(GT_OBJS) -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/


clean:
	rm -rf *.so
	rm -rf test
	rm -rf *.o
