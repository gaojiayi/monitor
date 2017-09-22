CUR_USER=`whoami`
IP=`/sbin/ifconfig eth0|awk '/inet /{print $2}'|tr -d "addr:"`
ps -ef | grep 'python' | grep -v 'grep' | grep -v 'usr' | grep -v 'service.py' | grep -v 'stop_all_monitor.py'  | grep ${CUR_USER}| awk '{print $2}' | while read pid1
do
 kill -9  ${pid1} 2>&1 >/dev/null
done
ps -ef | grep redis-cli.*3800.*MONITOR | grep -v grep |  grep ${CUR_USER}| awk '{print $2}' | while read pid2
do
 kill -9 ${pid2} 2>&1 >/dev/null
 echo "Stop Monitor success from $IP"
done
