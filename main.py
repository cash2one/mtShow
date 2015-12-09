#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Create by: Wang Songting
# Date Time: 2013-5-23 14:00:00
# Content:   main.py is responsible for initializing several Log services.
#
###############################################################################

from subprocess import *
import os,shutil,sys,socket
import settings
import time

class LogProject(object):
    def __init__(self,path,debug_flag):
        self.path = path
        self.pid_path = "%s/pid" % self.path
        self.loger = "%s/logserv.py" % self.path
        self.cront = "%s/crontsetexp.py" % self.path
        self.log_sock = 0
        self.log_sock_file = "%s/sock" % self.path
        self.log_proj_id = str(settings.DEVICE_ID)
        self.log_id_all = [conf[0] for conf in settings.SHOW_SERVER]
        self.log_id_dead = []
        self.log_is_dead = False
        self.debug_flag = debug_flag

    # Init IPC by AF_UNIX
    # Get Log service's result of Starting.
    def log_sock_init(self):
        try:
            self.sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
            self.sock.bind(self.log_sock_file)
            self.sock.settimeout(60)
            return True
        except Exception, e:
            print 'log_sock_init Err: %s' % e
            return False

    def log_sock_close(self):
        self.sock.close()
        os.remove(self.log_sock_file)

    def start_cron(self):
        Popen([self.cront])
    
    # Start each Log service.
    def start_log(self,id):
        Popen([self.loger,self.log_proj_id,id,self.debug_flag])
        try:
            # Waiting for Log service's result of Starting.
            msg,addr = self.sock.recvfrom(128)
            if msg == 'True':
                print 'Start Loger %s OK' % id
                return True
            else:
                print 'Start Loger %s Fail' % id
                return False
        except Exception, e:
            print 'Start Loger %s Fail' % id
            return False

    def read_pid(self,id):
        pid_file = open("%s/log%s.pid" % (self.pid_path,id),'r')
        pid = pid_file.readline().strip()
        return pid

    def kill_all(self):
        kill_argv = "kill -9 "
        for root,dirs,files in os.walk(self.pid_path):
            for pid_f in files:
                pid_file = open("%s/%s" % (self.pid_path,pid_f),'r')
                pid_argv = "%s " % pid_file.readline().strip()
                kill_argv += pid_argv
                print 'server x:pid(%s) is closing' % (pid_argv)
        if not kill_argv == "kill -9 ":
            Popen(kill_argv,shell=True)
        shutil.rmtree(self.pid_path)
        Popen("killall logserv.py", shell=True)
        time.sleep(1)

    def start(self):
        # if there is pid path, means Loger is running
        # So we can not start it again.
        if os.path.isdir(self.pid_path):
            print 'logers is running or pids exist'
            return False
        
        os.mkdir(self.pid_path)
        
        if not self.log_sock_init():
            print 'can not init loger socket'
            return False

        #start crontab job
        #self.start_cron()

        for id in self.log_id_all:
            print "starting log service ..."
            #start receive service
            flag = self.start_log(id)
            if not flag:
                self.kill_all()
                self.log_sock_close()
                return False
        self.log_sock_close()
        return True

    def stop(self):
        if not os.path.isdir(self.pid_path):
            return True

        self.kill_all()
        return True

    def restart(self):
        if not self.stop():
            return False
        if not self.start():
            return False
        return True

    def status(self):
        if not os.path.isdir(self.pid_path):
            return False

        for id in self.log_id_all:
            cur_pid = self.read_pid(id)

            # If some pid(s) is not running, record it's Loger id.
            # We will restart them.
            if not os.path.exists("/proc/%s" % cur_pid):
                self.log_is_dead = True
                self.log_id_dead.append(id)
                print 'server %s:pid(%s) is down' % (id,cur_pid)
            else:
                print 'server %s:pid(%s) is running' % (id,cur_pid)

        if not self.log_is_dead:
            return True
        
        if not self.log_sock_init():
            return False

        for id in self.log_id_dead:
            os.remove("%s/log%s.pid" % (self.pid_path,id))
            self.start_log(id)
            print 'recover server %s:pid(%s)' % (id,cur_pid)

        self.log_sock_close()


if __name__ == '__main__':
    
    path = os.path.abspath(os.path.dirname(__file__))
    proj = LogProject(path, settings.LOG_LEVEL)
    if len(sys.argv) < 2:
        print '''Example:
    ./main.py start|restart|stop|status
              '''
    else:
        if sys.argv[1] == 'start':
            if not proj.start():
                print "Start Proj Failed."
            else:
                print "Start Proj Successful."

        elif sys.argv[1] == 'stop':
            proj.stop()

        elif sys.argv[1] == 'restart':
            if not proj.restart():
                print "Restart Proj Failed."
            else:
                print "Restart Proj Successful."

        elif sys.argv[1] == 'status':
            proj.status()

        else:
            print "Unknown Arg......"
