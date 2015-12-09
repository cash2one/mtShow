#!/bin/bash
# 
# Create: Yuanji
# 2015/03/17
# Requied:  
#    Python2.7   
#    yum -y install boost
#

echo "-------------------"
echo "partchoice compile..."
echo "-------------------"
cd partchoice
make clean;make
cd ..


cd priceparser

echo "-------------------"
echo "amdecode compile..."
echo "-------------------"
cd amdecode
make clean;make
cd ..

echo "-------------------"
echo "baidecode compile..."
echo "-------------------"
cd baidecode
make clean;make
cd ..


echo "-------------------"
echo "shdecode compile..."
echo "-------------------"
cd shdecode
make clean;make
cd ..


echo "-------------------"
echo "tedecode compile..."
echo "-------------------"
cd tedecode
make clean;make
cd ..

echo "-------------------"
echo "jxdecode compile..."
echo "-------------------"
cd jxdecode
make clean;make
cd ..

echo "-------------------"
echo "gydecode compile..."
echo "-------------------"
cd gydecode
make clean;make
cd ..

echo "-------------------"
echo "ggdecode compile..."
echo "-------------------"
cd ggdecode
make clean;make
cd ..

cd ..
