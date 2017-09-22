#!/usr/bin/python
#coding=utf-8

from xml.dom.minidom import parse
import xml.dom.minidom
import threading
import time
import os
import time
import faina
import subprocess
import datetime
import signal
import socket
import logging  
import logging.handlers  
from socket import *

curr_time = time.strftime('%Y%m%d',time.localtime(time.time()))
def getLogger(): 
    LOG_FILE = '../log/oppf_monitor_'+time.strftime('%Y%m%d',time.localtime(time.time()))+'.log'
    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5)
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger=logging.getLogger('monitor')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

LOG = getLogger()


class alterThread(threading.Thread):
    def __init__(self,name=None):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        global LOG
        global curr_time
        while True :
            if curr_time == time.strftime('%Y%m%d',time.localtime(time.time())):
                pass
            else :
                curr_time= time.strftime('%Y%m%d',time.localtime(time.time()))
                LOG = getLogger()

class loggerThread(threading.Thread):
    def __init__(self,name=None,log=None,data=None):
        threading.Thread.__init__(self)
        self.name = name
        self.log = log
        self.data = data
    def run(self):
        LOG_FILE = '../log/oppf_monitor_'+time.strftime('%Y%m%d',time.localtime(time.time()))+'.log'  
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) 
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'  
        formatter = logging.Formatter(fmt)   
        handler.setFormatter(formatter)
        logger=logging.getLogger(self.log)      
        logger.addHandler(handler)           
        logger.setLevel(logging.DEBUG)  
        logger.info(self.data) 

def getLogFile():
    global LOG
    global curr_time
    if curr_time == time.strftime('%Y%m%d',time.localtime(time.time())):
        pass
    else :
        curr_time = time.strftime('%Y%m%d',time.localtime(time.time()))
        LOG = getLogger()

# obtain cycle socket service_path  and service_host   info from  xml
DOMTree = xml.dom.minidom.parse("../config/config.xml")
deployment = DOMTree.documentElement
service_hosts = deployment.getElementsByTagName("service_host")
monitors = deployment.getElementsByTagName("monitor_cycle")
sockets = deployment.getElementsByTagName("socket")

for service_host in service_hosts:
    if service_host.hasAttribute("name"):
        print "name:%s"% service_host.getAttribute("name")
    service_ip = service_host.getElementsByTagName('server_ip')[0].childNodes[0].data
#    service_port = service_host.getElementsByTagName('server_port')[0].childNodes[0].data
#    service_passwd = service_host.getElementsByTagName('server_passwd')[0].childNodes[0].data

for monitor in monitors:
    redis_cycle = monitor.getElementsByTagName('redis')[0].childNodes[0].data
    mongodb_cycle = monitor.getElementsByTagName('mongodb')[0].childNodes[0].data
    seda_cycle = monitor.getElementsByTagName('seda')[0].childNodes[0].data
    aiesb_cycle = monitor.getElementsByTagName('aiesb')[0].childNodes[0].data
    redis_key_cycle = monitor.getElementsByTagName('redis_key')[0].childNodes[0].data

socket_port = sockets[0].getElementsByTagName('socket_port')[0].childNodes[0].data



def TIMEOUT_COMMAND(command, timeout):  
    cmd = command.split(" ")  
    start = datetime.datetime.now()  
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
    while process.poll() is None:  
        time.sleep(0.2)  
        now = datetime.datetime.now()  
        if (now - start).seconds> timeout:  
            os.kill(process.pid, signal.SIGKILL)  
            os.waitpid(-1, os.WNOHANG)  
            return None  
    return process.stdout.readlines()

# the thread of update oracle: use this method have some problems .
class updateOracleThread(threading.Thread):
    def __init__(self,name=None,data=None):
        threading.Thread.__init__(self)
        self.name = name
        self.data = data
    def run(self):
        print(self.name+":insert into oracle options!")
        cursor.execute("insert into AOP_SYSTEM_MONITOR VALUES(:ADDRESS,:PORT,:MONITOR_OBJ,:MONITOR_TYPE,:MONITOR_VALUE,TO_DATE(:C_DATE,'yyyy-mm-dd hh:mi:ss'))",self.data)
	oracleConn.commit()

# the thread of update redis
class updateRedisThread(threading.Thread):
    def __init__(self,name=None,redisConn=None,key=None,value=None):
        threading.Thread.__init__(self)
	self.name = name
        self.key = key
        self.value = value
        self.redisConn = redisConn
    def run(self):
#        key = self.data['MONITOR_OBJ']+'^'+self.data['ADDRESS']+'^'+str(self.data['PORT'])+'^'+self.data['MONITOR_TYPE']
#       redisConn.set(key,self.data['MONITOR_VALUE'])
        self.redisConn.set(self.key,self.value)


#Order by monitor_obj to execute shell
class monitorThread(threading.Thread):
    def __init__(self,monitor_obj=None,time=10,port=0):
        threading.Thread.__init__(self)
        self.monitor_obj = monitor_obj
        self.time = time
        self.port = port
    def run(self):
        timer(self.monitor_obj,self.time,self.port)


# read shell script
def getDataFromShell(shell):
    print "./monitor_stats.sh "+shell
    return os.popen("./monitor_stats.sh "+shell).readlines()

def getRedisPorts():
    return os.popen("ps -ef | grep './redis-server' | grep -v grep | awk -F'*:' '{print $2}'").readlines()

def sendData():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    try:  
        port = int(socket_port)  
    except ValueError:  
        port = socket.getservbyname(socket_port, 'udp')     
    s.connect((service_ip, port))
    return s

socket_client = socket(AF_INET,SOCK_STREAM)
socket_client.connect((service_ip,int(socket_port))) 

lock = threading.Lock()
def sendAll(datas):
    if lock.acquire():
        try :
            socket_client.sendall(datas)
            result = socket_client.recv(1024)
        finally :
            lock.release()

def doTask(obj,port):
    MONGODB_MEMORY={}
    MONGODB_MEMORY_KEY=''
    MONGODB_CURSOR={}
    MONGODB_CURSOR_KEY=''
    REDIS_MEMORY={}
    REDIS_MEMORY_KEY=''
    REDIS_KEYS={}
    REDIS_KEYS_KEY=''
    SEDA_JVM={}
    SEDA_JVM_KEY=''
    SEDA_CPU={}
    SEDA_CPU_KEY=''
    AIESB_GC={}
    AIESB_GC_KEY=''
    AIESB_JVM={}
    AIESB_JVM_KEY=''
    S_DATE=''
    list=[]
    REDIS_MEMORY_DIC={}
    if obj.find('rediskeys') == 0 :
        S_DATE = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        TIMEOUT_COMMAND("./monitor_stats.sh redismonitor "+str(port),int(redis_key_cycle))
        os.popen("./monitor_stats.sh handerFile "+str(port))
        faina.faina_start("redis_monitor_"+str(port)+".log","redis_faina_"+str(port)+".txt")
        obj = obj+" "+str(port)
    for data in getDataFromShell(obj):
        if data.startswith('{'):
            LOG.info(data)
            pythonData = eval(data.strip('\n'))
            if pythonData['MONITOR_OBJ'] == 'MONGODB_MEMORY':
                pythonData['MONITOR_VALUE'] = round(float(pythonData['MONITOR_VALUE'])/1024,2)
                MONGODB_MEMORY[pythonData['MONITOR_TYPE']] = pythonData['MONITOR_VALUE']
                MONGODB_MEMORY['C_DATE'] = pythonData['C_DATE']
                MONGODB_MEMORY_KEY = 'MONGODB_MEMORY^'+pythonData['ADDRESS']+'^'+str(pythonData['PORT'])
            elif pythonData['MONITOR_OBJ'] == 'MONGODB_CURSOR':
                MONGODB_CURSOR[pythonData['MONITOR_TYPE']] = pythonData['MONITOR_VALUE']
                MONGODB_CURSOR['C_DATE'] = pythonData['C_DATE']
                MONGODB_CURSOR_KEY = 'MONGODB_CURSOR^'+pythonData['ADDRESS']+'^'+str(pythonData['PORT'])
            elif pythonData['MONITOR_OBJ'] == 'REDIS_MEMORY':
                pythonData['MONITOR_VALUE'] = round(float(pythonData['MONITOR_VALUE'])/1024/1024,2)
                REDIS_MEMORY[pythonData['MONITOR_TYPE']] = pythonData['MONITOR_VALUE']
                REDIS_MEMORY['C_DATE'] = pythonData['C_DATE']
                REDIS_MEMORY_KEY = 'REDIS_MEMORY^'+pythonData['ADDRESS']+'^'+str(pythonData['PORT'])
                REDIS_MEMORY_DIC[REDIS_MEMORY_KEY] = str(REDIS_MEMORY) 
            elif pythonData['MONITOR_OBJ'] == 'REDIS_KEYS':
                if pythonData['MONITOR_VALUE'] != '' :
                    REDIS_KEYS[pythonData['MONITOR_TYPE']] = pythonData['MONITOR_VALUE']
                REDIS_KEYS['C_DATE'] = pythonData['C_DATE']
                REDIS_KEYS['S_DATE'] = S_DATE
                pythonData['S_DATE'] = S_DATE
                REDIS_KEYS_KEY = 'REDIS_KEYS^'+pythonData['ADDRESS']+'^'+str(pythonData['PORT'])
            elif pythonData['MONITOR_OBJ'] == 'SEDA_CPU':
                SEDA_CPU[pythonData['MONITOR_TYPE']] = pythonData['MONITOR_VALUE']
                SEDA_CPU['C_DATE'] = pythonData['C_DATE']
                SEDA_CPU_KEY = 'SEDA_CPU^'+pythonData['ADDRESS']
            elif pythonData['MONITOR_OBJ'] == 'SEDA_JVM':
                pythonData['MONITOR_VALUE'] = round(float(pythonData['MONITOR_VALUE'])/1024/1024,2)
                SEDA_JVM[pythonData['MONITOR_TYPE']] = pythonData['MONITOR_VALUE']
                SEDA_JVM['C_DATE'] = pythonData['C_DATE']
                SEDA_JVM_KEY = 'SEDA_JVM^'+pythonData['ADDRESS']
            elif pythonData['MONITOR_OBJ'] == 'AIESB_JVM':
                pythonData['MONITOR_VALUE'] = round(float(pythonData['MONITOR_VALUE'])/1024/1024,2)
                AIESB_JVM[pythonData['MONITOR_TYPE']] = pythonData['MONITOR_VALUE']
                AIESB_JVM['C_DATE'] = pythonData['C_DATE']
                AIESB_JVM_KEY = 'AIESB_JVM^'+pythonData['ADDRESS']
            elif pythonData['MONITOR_OBJ'] == 'AIESB_GC':
                AIESB_GC[pythonData['MONITOR_TYPE']] = pythonData['MONITOR_VALUE']
                AIESB_GC['C_DATE'] = pythonData['C_DATE']
                AIESB_GC_KEY = 'AIESB_GC^'+pythonData['ADDRESS']
            else:
                print "Not Find Monitor Object!"
            list.append(pythonData)

    if obj == 'redis' :
        for k,v in REDIS_MEMORY_DIC.items():
            sendAll(k+"&"+v)
    elif  obj.find('rediskeys') == 0 :
        sendAll(REDIS_KEYS_KEY+"&"+str(REDIS_KEYS))
    elif obj == 'mongodb':
        sendAll(MONGODB_CURSOR_KEY+"&"+str(MONGODB_CURSOR))
        sendAll(MONGODB_MEMORY_KEY+"&"+str(MONGODB_MEMORY))
    elif obj == 'seda':
        sendAll(SEDA_JVM_KEY+"&"+str(SEDA_JVM))
        sendAll(SEDA_CPU_KEY+"&"+str(SEDA_CPU))
    elif obj == 'aiesb':
        sendAll(AIESB_JVM_KEY+"&"+str(AIESB_JVM))
        sendAll(AIESB_GC_KEY+"&"+str(AIESB_GC))
    else :
        print "Error,can not monit other object!"
    for i in range(len(list)):
        sendAll(str(list[i]))
        

def timer(obj,n,port):
    while True:
        try:
            getLogFile()
            doTask(obj,port)
        except Exception,ex:
            LOG.info("Exception:"+str(ex))
        if n > 0:
            time.sleep(n)

if __name__=='__main__':
    try:
        #alterThread('').start()
        for data in getRedisPorts():
            monitorThread("rediskeys ",0,data.strip('\n')).start()
        for data in getRedisPorts():
            monitorThread("redis",int(redis_cycle),0).start()
            break
        if os.popen("ps -ef |grep -v grep | grep mongodb").read() != '' :
            monitorThread("mongodb",int(mongodb_cycle),0).start()
        if  os.popen("ps -ef | grep -v grep| grep java |grep oppf_esb ").read() != '' :
            monitorThread("aiesb",int(aiesb_cycle),0).start()
        if  os.popen("ps -ef | grep -v grep| grep java |grep seda ").read() != '' :
            monitorThread("seda",int(seda_cycle),0).start()
    except Exception,ex:
        print ex
        LOG.info(str(ex))
       
    

  

 
