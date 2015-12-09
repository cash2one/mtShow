#Geo Polymerization Technology Co, Ltd

#DSP-iShow

#CREATE Songting

#UPDATE v3.3 Yuanji
    1. 添加make.sh,新部署的机器需要安装c++ boost库，然后./make.sh
    2. 修改点击到达 cpahandler -> arrihandler
    3. 添加新字段
    4. 

#BUILD
    ./make.sh

#USAGE
    python main.py start/restart/stop

#LOG
    /var/log/istream/comm.log

#ATTENTION
    启动失败，如果当前目录下有sock，删除后重新启动；

