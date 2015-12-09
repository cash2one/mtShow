# Copyright 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

CFLAGS = -g -Wall
CC = g++
LIBS = -lssl

all: decrypter ggdecode.so

ggdecode.so:decrypter.o src4py.o
	g++ src4py.o -o ggdecode.so -shared -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ -L/usr/local/lib/python2.7/ -L/usr/local/lib/ -lboost_python -lssl
decrypter.o:
	g++ -c decrypter.cc -o decrypter.o -lcrypto 
src4py.o:decrypter.o
	g++ -c src4py.cpp -o src4py.o -fPIC -I /usr/local/include/python2.7/ -I /usr/local/include/boost/ 

decrypter: decrypter.o
	${CC} ${CFLAGS} decrypter.o -o $@ ${LIBS}

#decrypter.o: decrypter.cc
#	${CC} ${CFLAGS} -c decrypter.cc

clean:
	rm -rf decrypter.o decrypter src4py.o ggdecode.so

run: decrypter
	./decrypter
