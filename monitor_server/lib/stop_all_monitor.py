#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
# filename: pexpect_test.py  
''''' 
Created on 2010-7-2 
 
@author: forever 
'''  
import pexpect  
from xml.dom.minidom import parse
import xml.dom.minidom
import os
import paramiko
import threading

DOMTree = xml.dom.minidom.parse("../config/config.xml")
deployment = DOMTree.documentElement
client_hosts = deployment.getElementsByTagName("client_host")
client_path = deployment.getElementsByTagName("client_path")[0].getElementsByTagName('client_dir')[0].childNodes[0].data

def ssh2(ip,username,passwd,cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,passwd,timeout=5)
        for m in cmd:
            ssh.exec_command(m)
#            stdin, stdout, stderr = ssh.exec_command(m)
#           stdin.write("Y")
#            out = stdout.readlines()
#            for o in out:
#                print o,
        print '%s\tOK\n'%(ip)
        ssh.close()
    except :
        print '%s\tError\n'%(ip)


if __name__=='__main__':
    cmd = ['cd '+client_path+'/bin;sh monitor_stop.sh']
    for client_host in client_hosts :
	ips = client_host.getElementsByTagName('client_ip')[0].childNodes[0].data
        username = client_host.getElementsByTagName('client_user')[0].childNodes[0].data
        passwd = client_host.getElementsByTagName('client_passwd')[0].childNodes[0].data
        print "Begin......"
        for ip in ips.split(','):
            a=threading.Thread(target=ssh2,args=(ip,username,passwd,cmd))
            a.start() 
