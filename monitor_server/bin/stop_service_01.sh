#!/bin/sh
CUR_USER=`whoami`
IP=`/sbin/ifconfig eth0|awk '/inet /{print $2}'|tr -d "addr:"`
ps -ef | grep 'python service.py' | grep -v 'grep' | grep -v 'usr' | awk '{print $2}' | while read pid1
do
 kill -9 ${pid1} 2>&1 >/dev/null
 echo "Stop scoket service from $IP successfully"
done
ps -ef | grep 'python' | grep -v 'grep' | grep -v 'usr' | awk '{print $2}' | while read pid2
do
 kill -9 ${pid2} 2>&1 >/dev/null
done
