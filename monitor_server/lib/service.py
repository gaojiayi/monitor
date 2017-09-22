#!/usr/bin/python
#coding=utf-8

from xml.dom.minidom import parse
import xml.dom.minidom
import threading
import time
import cx_Oracle
import redis
import os
import time
import subprocess
import datetime
import signal
import socket
import traceback 
from DBUtils.PooledDB import PooledDB
import logging  
import logging.handlers
import SocketServer  
from SocketServer import StreamRequestHandler as SRH  
from time import ctime 
import threadpool

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

def getLogFile():
    global LOG
    global curr_time
    if curr_time == time.strftime('%Y%m%d',time.localtime(time.time())):
        pass
    else :
        curr_time = time.strftime('%Y%m%d',time.localtime(time.time()))
        LOG = getLogger()
        delDataOfOrcl()

class alterThread(threading.Thread):
    def __init__(self,name=None):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        while True :
            if curr_time == time.strftime('%Y%m%d',time.localtime(time.time())):
                pass
            else :
                global LOG
                LOG = getLogger()

class loggerThread(threading.Thread):
    def __init__(self,name=None,data=None):
        threading.Thread.__init__(self)
        self.name = name
        #self.log = log
        self.data = data
    def run(self):
        LOG_FILE = '../log/oppf_monitor_'+time.strftime('%Y%m%d',time.localtime(time.time()))+'.log'  
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) 
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'  
        formatter = logging.Formatter(fmt)   
        handler.setFormatter(formatter)      
        logger =logging.getLogger('monitor')    
        logger.addHandler(handler)           
        logger.setLevel(logging.DEBUG)  
        logger.info(self.data)
  

# obtain redis and oracle  connection info from  xml
DOMTree = xml.dom.minidom.parse("../config/config.xml")
deployment = DOMTree.documentElement

oracles = deployment.getElementsByTagName("oracle")
rediss = deployment.getElementsByTagName("redis_config")
socket_port = deployment.getElementsByTagName("socket")[0].getElementsByTagName('socket_port')[0].childNodes[0].data
server_ip = deployment.getElementsByTagName("service_host")[0].getElementsByTagName('server_ip')[0].childNodes[0].data
days = deployment.getElementsByTagName("save_days")[0].getElementsByTagName('days')[0].childNodes[0].data
#host = '' # Bind to all interfaces   
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#s.bind((host, int(socket_port)))

thread_pool = threadpool.ThreadPool(10)
def thread_task(datas):
    LOG.info(datas)
    if  not  datas.startswith("{"):
        LOG.info("====================insert into redis===========================")
        updateRedis(datas.split('&')[0],datas.split('&')[1])
    else :
        LOG.info("====================insert into oracle===========================")
        updateOracle(eval(datas))
      


class Servers(SRH):  
    def handle(self):  
        while True:  
            getLogFile()
            message = self.request.recv(8096)
            print message
            if not message:   
                break  
            print "RECV from ", self.client_address[0] 
            L =[]
            L.append(message) 
            requests = threadpool.makeRequests(thread_task, L)
            [thread_pool.putRequest(req) for req in requests]  
            thread_pool.wait() 
            self.request.send("ok")

for oracle in oracles:
    if oracle.hasAttribute("name"):
        print "name:%s"% oracle.getAttribute("name")
    orcl_user  = oracle.getElementsByTagName('orcl_user')[0].childNodes[0].data
    orcl_pwd = oracle.getElementsByTagName('orcl_pwd')[0].childNodes[0].data
    orcl_sid = oracle.getElementsByTagName('orcl_sid')[0].childNodes[0].data
    orcl_host = oracle.getElementsByTagName('orcl_host')[0].childNodes[0].data
    orcl_port = oracle.getElementsByTagName('orcl_port')[0].childNodes[0].data


for res in rediss:
    host = res.getElementsByTagName('redis_host')[0].childNodes[0].data
    port = res.getElementsByTagName('redis_port')[0].childNodes[0].data
    db = res.getElementsByTagName('redis_db')[0].childNodes[0].data

# get oracle connection
def getOracleConn():
    return cx_Oracle.connect(conn.childNodes[0].data)
#oracleConn = getOracleConn()

# get redis connection
def getRedisConn():
    return redis.Redis(host=host,port=int(port),db=int(db))
redisConn = getRedisConn()
#redisPool = redis.ConnectionPool(host = host,port = int(port),db = int(db))

pool = PooledDB(cx_Oracle,user = orcl_user,password = orcl_pwd,dsn = "%s:%s/%s" %(orcl_host,orcl_port,orcl_sid),mincached=20,maxcached=200)

class Ora():
    __pool = None #connection object
    def __init__(self):
        self.pool = Ora.__getConn()
        self.cursor = self.conn.cursor()

    @staticmethod
    def __getConn():
        if Ora.__pool is None:
            Ora.__pool = PooledDB(cx_Oracle,user = orcl_user,password = orcl_pwd,dsn = "%s:%s/%s" %(orcl_host,orcl_port,orcl_sid),mincached=20,maxcached=200)
        return __pool.connection()

    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()
        self.close()

    def execute(self, sql, args = {}):
        try:
            return self.cursor.execute(sql, args)
        except Exception,e:
            self.close()
            raise e

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
        global pool
        conn = pool.connection()
        cur = conn.cursor()
        self.data['MONITOR_VALUE'] = str(self.data['MONITOR_VALUE'])
        if self.data['MONITOR_OBJ'] == 'REDIS_KEYS':
            if self.data['MONITOR_TYPE'] != "" : 
                cur.execute("insert into AOP_SYSTEM_MONITOR VALUES(:ADDRESS,:PORT,:MONITOR_OBJ,:MONITOR_TYPE,:MONITOR_VALUE,TO_DATE(:C_DATE,'yyyy-mm-dd hh24:mi:ss'),TO_DATE(:S_DATE,'yyyy-mm-dd hh24:mi:ss'))",self.data)
        else:
            cur.execute("insert into AOP_SYSTEM_MONITOR(ADDRESS,PORT,MONITOR_OBJ,MONITOR_TYPE,MONITOR_VALUE,C_DATE)  VALUES(:ADDRESS,:PORT,:MONITOR_OBJ,:MONITOR_TYPE,:MONITOR_VALUE,TO_DATE(:C_DATE,'yyyy-mm-dd hh24:mi:ss'))",self.data)
        conn.commit()
        cur.close()
        conn.close()

def updateOracle(data):
    global pool
    conn = pool.connection()
    cur = conn.cursor()
    data['MONITOR_VALUE'] = str(data['MONITOR_VALUE'])
    if data['MONITOR_OBJ'] == 'REDIS_KEYS':
        if data['MONITOR_TYPE'] != "" :
            cur.execute("insert into AOP_SYSTEM_MONITOR VALUES(:ADDRESS,:PORT,:MONITOR_OBJ,:MONITOR_TYPE,:MONITOR_VALUE,TO_DATE(:C_DATE,'yyyy-mm-dd hh24:mi:ss'),TO_DATE(:S_DATE,'yyyy-mm-dd hh24:mi:ss'))",data)
    else:
        cur.execute("insert into AOP_SYSTEM_MONITOR(ADDRESS,PORT,MONITOR_OBJ,MONITOR_TYPE,MONITOR_VALUE,C_DATE)  VALUES(:ADDRESS,:PORT,:MONITOR_OBJ,:MONITOR_TYPE,:MONITOR_VALUE,TO_DATE(:C_DATE,'yyyy-mm-dd hh24:mi:ss'))",data)
    conn.commit()
    cur.close()
    conn.close()

def delDataOfOrcl():
    global pool
    conn = pool.connection()
    cur = conn.cursor()
    cur.execute("delete from aop_system_monitor  where C_DATE  <  sysdate-"+days);
    conn.commit()
    cur.close()
    conn.close()



# the thread of update redis
class updateRedisThread(threading.Thread):
    def __init__(self,name=None,key=None,value=None):
        threading.Thread.__init__(self)
	self.name = name
        self.key = key
        self.value = value
    def run(self):
        #redis.Redis(connection_pool = redisPool).set(self.key,self.value)
        redisConn.set(self.key,self.value)

def updateRedis(key,value):
    redisConn.set(key,value)

if __name__=='__main__':
    print "Scoket service start successfully!"
    try:
        server = SocketServer.ThreadingTCPServer((server_ip,int(socket_port)),Servers)  
        server.serve_forever() 
    except socket.error as (code, msg):
        pass
#        if code != errno.EINTR:
#            raise      
    except (KeyboardInterrupt, SystemExit):
        print "raise"
        raise
    except Exception,ex:
        print "traceback"
        traceback.print_exc()
        LOG.info("Exception:"+str(ex))
       
    

  

 
