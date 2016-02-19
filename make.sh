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
echo "baidecode compile..."
echo "-------------------"
cd baidecode
make clean;make
cd ..


echo "-------------------"
echo "jxdecode compile..."
echo "-------------------"
cd jxdecode
make clean;make
cd ..

cd ..
