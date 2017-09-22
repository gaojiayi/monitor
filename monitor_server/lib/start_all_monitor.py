#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
# filename: start_all_monitor.py  
'''
Created on 2016-6-29
 
@author: gaojy
'''  
import pexpect  
import paramiko
from xml.dom.minidom import parse
import xml.dom.minidom
import threading
import time

DOMTree = xml.dom.minidom.parse("../config/config.xml")
deployment = DOMTree.documentElement

client_hosts = deployment.getElementsByTagName("client_host")
service_path = deployment.getElementsByTagName("service_path")[0].getElementsByTagName('server_dir')[0].childNodes[0].data
client_path = deployment.getElementsByTagName("client_path")[0].getElementsByTagName('client_dir')[0].childNodes[0].data

def ssh2(ip,user,passwd,cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,user,passwd,timeout=5)
        for m in cmd:
            ssh.exec_command(m)
#            stdin, stdout, stderr = ssh.exec_command(m)
#            stdin.write("Y")   
#            out = stdout.readlines()
#            for o in out:
#                print o,
        print '%s\tOK\n'%(ip)
        ssh.close()
    except :
        print '%s\tError\n'%(ip)

class startMonitorThread(threading.Thread):
    def __init__(self,name=None,ip=None,user=None,passwd=None,catalog=None,cmd=None):
        threading.Thread.__init__(self)
        self.name = name
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.catalog = catalog
        self.cmd = cmd

    def run(self):
        child = pexpect.spawn('ssh %s@%s' % (self.user,self.ip))
        child.expect ('password:')
        child.sendline (self.passwd)
        child.expect('$') 
        child.sendline('sudo -s')
        child.expect (':')
        child.sendline (self.passwd)
        child.expect('#') 
        child.sendline('cd '+self.catalog)
        child.expect('#') 
        child.sendline(self.cmd)
        child.interact()     # Give control of the child to the user.

if __name__ == '__main__':  
    cmd = ['cd ' +client_path+'/lib;python client.py']	
    for client_host in client_hosts :
        ips = client_host.getElementsByTagName('client_ip')[0].childNodes[0].data
        user = client_host.getElementsByTagName('client_user')[0].childNodes[0].data
        passwd = client_host.getElementsByTagName('client_passwd')[0].childNodes[0].data
        for ip in ips.split(','):
            print "Upload config.xml to %s"% ip
            t = paramiko.Transport((ip,22))
            t.connect(username = user,password = passwd)
            sftp = paramiko.SFTPClient.from_transport(t)
            sftp.put(service_path+"/config/config.xml",client_path+"/config/config.xml")
            t.close()
            print "Monitor starts from %s"% ip
            # monitor = startMonitorThread('',ip,user,passwd,client_path+'/lib','python client.py')
            monitor = threading.Thread(target=ssh2,args=(ip,user,passwd,cmd))
            monitor.start()
    print "All monitor finish start!"    
 
