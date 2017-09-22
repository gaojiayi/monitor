#!/bin/bash

function sudouser()
{
   echo "$2" |su -c "$3" "$1"
}

function getParam()
{
        cat ../config/config.xml | grep "<$1>" | tr -d "/" | awk -F"<$1>" '{print $2}'

}

function esbjstat()
{
        esbuser=`getParam aiesb_user`
        esbpasswd=`getParam aiesb_passwd`
        sudouser ${esbuser} ${esbpasswd} "$1"
}

function sedajstat()
{
        sedauser=`getParam seda_user`
        sedapasswd=`getParam seda_passwd`
        sudouser ${sedauser} ${sedapasswd} "$1"
}


function sourcePath(){
   export  PATH=${HOME}/mongodb/app/mongodb-linux-x86_64-2.6.6/bin:$PATH
   export  PATH=${HOME}/redis/bin:$PATH
   export  PATH=${HOME}/bin:$PATH
}

function pubParam(){
	#IP=`/sbin/ifconfig eth0|awk '/inet addr/{print $2}'|tr -d "addr:"`
	IP=`/sbin/ifconfig eth0|awk '/inet /{print $2}'|tr -d "addr:"`
	# you need insert all mongodb`s ports in the parameter of MONGODB_PORT . And use " " split them. 
	MONGODB_PORT=(38200)
}
function mongodb_stats(){
for PORT in $MONGODB_PORT
do
mongo ${IP}:${PORT}/esb <<EOF>1.log
db.serverStatus ( )
exit
EOF
C_DATE=$(date +"%Y-%m-%d %H:%M:%S")
RES=`cat 1.log | grep -A 6 '"mem" : {' | tr -s "," " "|grep resident|awk -F":" '{print $2}'`
VSIZE=`cat 1.log | grep -A 6 '"mem" : {' | tr -s "," " "|grep virtual|awk -F":" '{print $2}'`
MAPPED=`cat 1.log | grep -A 6 '"mem" : {' | tr -s "," " "|grep mapped|awk -F":" '{print $2}'`
CURSORS=`cat 1.log | grep -A 6 "cursors" | tr -s "," " "|grep totalOpen|awk -F":" '{print $2}'`
#mongo ${IP}:38200/esb <<EOF>1.log
#db.stats ( )
#exit
#EOF
#COLLECTIONS=`cat 1.log | egrep "collections|dataSize|storageSize" | tr -s "," " "|grep collections|awk -F":" '{print $2}'`
#DATA_SIZE=`cat 1.log | egrep "collections|dataSize|storageSize" | tr -s "," " "|grep dataSize|awk -F":" '{print $2}'`
#STORAGE_SIZE=`cat 1.log | egrep "collections|dataSize|storageSize" | tr -s "," " "|grep storageSize|awk -F":" '{print $2}'`
echo "{\"ADDRESS\":\"${IP}\",\"PORT\":${PORT},\"MONITOR_OBJ\":\"MONGODB_MEMORY\",\"MONITOR_TYPE\":\"RES\",\"MONITOR_VALUE\":${RES},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":${PORT},\"MONITOR_OBJ\":\"MONGODB_MEMORY\",\"MONITOR_TYPE\":\"VSIZE\",\"MONITOR_VALUE\":${VSIZE},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":${PORT},\"MONITOR_OBJ\":\"MONGODB_MEMORY\",\"MONITOR_TYPE\":\"MAPPED\",\"MONITOR_VALUE\":${MAPPED},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":${PORT},\"MONITOR_OBJ\":\"MONGODB_CURSOR\",\"MONITOR_TYPE\":\"QUERY\",\"MONITOR_VALUE\":${CURSORS},\"C_DATE\":\"${C_DATE}\"}"  
#current_connections:$CUR_CONN 
#available_connections:$AVL_CONN 
#collections:$COLLECTIONS 
#dataSize:$DATA_SIZE 
#storageSize:$STORAGE_SIZE
rm -rf 1.log
done
}

function redis_stats(){
for  REDIS_PORT in `ps -ef | grep './redis-server' | grep -v grep | awk -F'*:' '{print $2}'`
do
redis-cli -h ${IP}  -p ${REDIS_PORT} info > 2.log
dos2unix 2.log
REDIS_ALL_MEM=`cat 2.log | grep -e "used_memory_rss" | awk -F ':' '{print $2}'`
REDIS_USED_MEM=`cat 2.log | grep -e "used_memory:" | awk -F ':' '{print $2}'`
REDIS_KEYS=`cat 2.log | grep -e "db0:keys" | awk -F ':' '{print $2}' | awk -F ',' '{print $1}' | awk -F '=' '{print $2}'`
C_DATE=$(date +"%Y-%m-%d %H:%M:%S")
echo "{\"ADDRESS\":\"${IP}\",\"PORT\":${REDIS_PORT},\"MONITOR_OBJ\":\"REDIS_MEMORY\",\"MONITOR_TYPE\":\"USED_MEM\",\"MONITOR_VALUE\":${REDIS_USED_MEM},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":${REDIS_PORT},\"MONITOR_OBJ\":\"REDIS_MEMORY\",\"MONITOR_TYPE\":\"ALL_MEM\",\"MONITOR_VALUE\":${REDIS_ALL_MEM},\"C_DATE\":\"${C_DATE}\"}"
rm -rf 2.log
done
}

#need port 
function redis_monitor(){
redis-cli -p $1  MONITOR > redis_${1}.log
}

function handerFile(){
ps -ef | grep "redis-cli.*${1}.*MONITOR" | grep -v grep | awk '{print $2}' | while read pid2
do
 kill -9 ${pid2} 2>&1 >/dev/null
done
cat redis_${1}.log | egrep  '] "SET"|] "GET"' | awk '{print $1, $2, $3, $4, $5}' > redis_monitor_${1}.log
}
# only need port
function redis_keys_stats(){
#S_DATE=$3
S_DATE=$(date +"%Y-%m-%d %H:%M:%S")
#redis-cli -p $1  MONITOR | head -n $2  | ./redis-faina/redis-faina.py  --redis-version=2.8 | egrep -v  '===|Top Keys' > redis_keys_${1}.log
#cat -A redis_keys_${1}.log | sed 's/\^I/ /g' > redis_keys_${2}${1}.log
#REDIS_KEYS=""
C_DATE=$(date +"%Y-%m-%d %H:%M:%S")
Flag="no"
while read line
do
Flag="yes"
KEY=`echo $line | awk '{print $1}'`
COUNT=`echo $line | awk '{print $2}'`
if [ "$KEY" != "$" ]&&[ "$KEY" != "0" ]&&[ "$KEY" != "n/a$" ]; then
echo "{\"ADDRESS\":\"${IP}\",\"PORT\":$1,\"MONITOR_OBJ\":\"REDIS_KEYS\",\"MONITOR_TYPE\":\"${KEY}\",\"MONITOR_VALUE\":${COUNT},\"C_DATE\":\"${C_DATE}\",\"S_DATE\":\"\"}"
REDIS_KEYS="${REDIS_KEYS}${KEY}=${COUNT},"
fi
done < redis_faina_${1}.txt
if [ "$Flag" == "no" ]; then
echo "{\"ADDRESS\":\"${IP}\",\"PORT\":$1,\"MONITOR_OBJ\":\"REDIS_KEYS\",\"MONITOR_TYPE\":\"${KEY}\",\"MONITOR_VALUE\":\"${COUNT}\",\"C_DATE\":\"${C_DATE}\",\"S_DATE\":\"\"}"
fi
REDIS_KEYS="${REDIS_KEYS%?}"
#echo "{\"ADDRESS\":\"${IP}\",\"PORT\":$1,\"MONITOR_OBJ\":\"REDIS\",\"MONITOR_TYPE\":\"REDIS_KEYS\",\"MONITOR_VALUE\":\"${REDIS_KEYS}\",\"C_DATE\":\"${C_DATE}\",\"S_DATE\":\"${S_DATE}\"}"
#rm -rf ${1}.log
#rm -rf 4${1}.log
}

function seda_stats(){
SEDA_PID=`ps -ef | grep -v grep | grep 'seda.*jdk' | awk '{print $2'}`
sedajstat "jmap -heap ${SEDA_PID}" > 5.log
C_DATE=$(date +"%Y-%m-%d %H:%M:%S")
SEDA_EDEN=`cat 5.log | grep -A 4 'Eden Space:' | grep 'used' |awk '{print $3}'`
SEDA_SUR0=`cat 5.log | grep -A 4 'From Space:' | grep 'used' |awk '{print $3}'`
SEDA_SUR1=`cat 5.log | grep -A 4 'To Space:' | grep 'used' |awk '{print $3}'`
SEDA_OLD=`cat 5.log | grep -A 4 'PS Old Generation' | grep 'used' |awk '{print $3}'`
SEDA_PERM=`cat 5.log | grep -A 4 'PS Perm Generation' | grep 'used' |awk '{print $3}'`
#SEDA_CPU=`top -n 1 -p ${SEDA_PID}  | head -8 | tail -1 | awk '{print $9}'`
SEDA_CPU=`top -n 1 -p ${SEDA_PID} | head -8 | tail -1 | awk -F'seda' '{print $2}' | awk '{print $7}'`
# cat /proc/10502/status|grep -e VmRSS
# top -n 1 -p 10502  | awk '{if($0!=""){T=$0}} END {print $T}' 
# top -n 1 -p 10502  | head -8 | tail -1 | awk '{print $9}'
 echo	"{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"SEDA_JVM\",\"MONITOR_TYPE\":\"EDEN\",\"MONITOR_VALUE\":${SEDA_EDEN},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"SEDA_JVM\",\"MONITOR_TYPE\":\"SURVIVOR0\",\"MONITOR_VALUE\":${SEDA_SUR0},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"SEDA_JVM\",\"MONITOR_TYPE\":\"SURVIVOR1\",\"MONITOR_VALUE\":${SEDA_SUR1},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"SEDA_JVM\",\"MONITOR_TYPE\":\"OLD\",\"MONITOR_VALUE\":${SEDA_OLD},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"SEDA_JVM\",\"MONITOR_TYPE\":\"PERM\",\"MONITOR_VALUE\":${SEDA_PERM},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"SEDA_CPU\",\"MONITOR_TYPE\":\"CPU\",\"MONITOR_VALUE\":\"${SEDA_CPU}\",\"C_DATE\":\"${C_DATE}\"}"
rm -rf 5.log

}

function aiesb_stats(){
AIESB_PID=`ps -ef | grep -v grep| grep java |grep 'aiesb.*ESBDeployerListener' | grep -v Sandboxie | awk '{print $2}'`
esbjstat "jmap -heap ${AIESB_PID}" > 6.log
AIESB_EDEN=`cat 6.log | grep -A 4 'Eden Space:' | grep 'used' |awk '{print $3}'`
AIESB_SUR0=`cat 6.log | grep -A 4 'From Space:' | grep 'used' |awk '{print $3}'`
AIESB_SUR1=`cat 6.log | grep -A 4 'To Space:' | grep 'used' |awk '{print $3}'`
AIESB_OLD=`cat 6.log | grep -A 4 'PS Old Generation' | grep 'used' |awk '{print $3}'`
AIESB_PERM=`cat 6.log | grep -A 4 'PS Perm Generation' | grep 'used' |awk '{print $3}'`
esbjstat "jstat -gcutil ${AIESB_PID}" > 7.log
AIESB_YGC=`cat 7.log | tail -1 | awk '{print $6}'`
AIESB_FGC=`cat 7.log | tail -1 | awk '{print $8}'`
C_DATE=$(date +"%Y-%m-%d %H:%M:%S")
# /opt/jdk1.6.0_24/bin/jmap -heap 24964 | grep -3 'PS Young Generation' | grep 'used' |awk '{print $3}'
 echo	"{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"AIESB_JVM\",\"MONITOR_TYPE\":\"EDEN\",\"MONITOR_VALUE\":${AIESB_EDEN},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"AIESB_JVM\",\"MONITOR_TYPE\":\"SURVIVOR0\",\"MONITOR_VALUE\":${AIESB_SUR0},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"AIESB_JVM\",\"MONITOR_TYPE\":\"SURVIVOR1\",\"MONITOR_VALUE\":${AIESB_SUR1},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"AIESB_JVM\",\"MONITOR_TYPE\":\"OLD\",\"MONITOR_VALUE\":${AIESB_OLD},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"AIESB_JVM\",\"MONITOR_TYPE\":\"PERM\",\"MONITOR_VALUE\":${AIESB_PERM},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"AIESB_GC\",\"MONITOR_TYPE\":\"YGC\",\"MONITOR_VALUE\":${AIESB_YGC},\"C_DATE\":\"${C_DATE}\"}
{\"ADDRESS\":\"${IP}\",\"PORT\":\"\",\"MONITOR_OBJ\":\"AIESB_GC\",\"MONITOR_TYPE\":\"FGC\",\"MONITOR_VALUE\":${AIESB_FGC},\"C_DATE\":\"${C_DATE}\"}"
 rm -rf 6.log
 rm -rf 7.log
}
sourcePath
pubParam
if [ "$#" -lt 1 ]; then
echo "You need to input more than one parameter!"
exit 1
fi
if [ "$1" == "redis" ]||[ "$1" == "REDIS" ]; then
redis_stats 
elif [ "$1" == "mongodb" ]||[ "$1" == "MONGODB" ]; then
mongodb_stats 
elif [ "$1" == "SEDA" ]||[ "$1" == "seda" ]; then
seda_stats
elif [ "$1" == "aiesb" ]||[ "$1" == "AIESB" ]; then
aiesb_stats
elif [ "$1" == "REDISKEYS" ]||[ "$1" == "rediskeys" ]; then
redis_keys_stats $2  
elif [ "$1" == "redismonitor" ]||[ "$1" == "REDISMONITOR" ]; then
redis_monitor $2
elif [ "$1" == "handerFile" ]; then 
handerFile $2
else
echo "Parameters error!"
fi
