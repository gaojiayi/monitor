简介：

	集群间应用运行的健康状态数据定时采集监控，用于前台展示，和告警处理。主要针对ESB和Seda的GC情况，堆大小，mongodb的内存使用，redis内存使用情况，redis键的使用频率使用shell进行数据采集，并python发送到服务端。服务端主要多线程接收处理数据，并完成历史数据oracle入库，最新数据的redis入库。并且实时输出运行日志，服务端完成统一配置管理及启停服务等功能。


部署安装：

1.各主机需开启SSH，SFTP服务
2.在入库端安装：
  1）cx_oracle
   $rpm -ivh cx_Oracle-5.1.2-11g-py27-1.x86_64.rpm 
   $ls /usr/lib/python2.7/site-packages/cx_Oracle.so #有这个文件表示安装成功,根据python安装位置调整前端部分。
  2）oracle客户端  具体参照：http://www.tbdazhe.com/archives/602
   $unzip basic-11.1.0.70-linux-x86_64.zip
   $cd instantclient_11_1
   $cp * /usr/lib   #直接放到动态库搜索路径中，不需要额外的环境配置
   或
   $unzip basic-11.1.0.70-linux-x86_64.zip
   $cp -rf instantclient_11_1 /opt/
   $vi /etc/profile
      export ORACLE_HOME=/opt/instantclient_11_1
　　  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME
 
   $source /etc/profile
  3）redis模块
    tar -zvxf redis-2.8.0.tar.gz
    mv redis-2.8.0 python-redis-2.8.0
    cd python-redis-2.8.0
    python setup.py install
  4）paramiko模块（先安装 PyCrypto） 具体参照：http://www.cnblogs.com/xia520pi/p/3805043.html
    tar -zxvf pycrypto-2.6.tar.gz
    cd pycrypto-2.6/
    python setup.py build && python setup.py install

    tar xvzf paramiko-1.7.7.1.tar.gz
    cd paramiko-1.7.7.1/
    python setup.py build && python setup.py install
   
   5）Pexpect模块安装
    tar xzf pexpect-2.3.tar.gz
    cd pexpect-2.3
    sudo python ./setup.py install
    
   6)安装pooledDB连接池模块
     tar -zxvf DBUtils-1.1.tar
     cd DBUtils-1.1
     python setup.py install
   7)安装threadpool模块
     tar -jxvf  threadpool-1.3.2.tar.bz2
     cd threadpool-1.3.2/
     python setup.py install

3.脚本部署 ：在监控机器上，相同的目录下放置monitor_service文件夹内的所有脚本。在monitor_node机器上放置入库端文件夹内的所有脚本。
                 

4.启动脚本前配置：
  config.xml ：配置oracle数据源，redis连接，入库端脚本目录，监控端脚本目录，socket端口，监控端用户信息和服务端用户信息，以及各监控对象的周期时间。
  
  monitor_stat.sh  ：配置jdk，mongodb，redis的安装bin目录。

5.启动
  1)启动socket服务端
   cd bin 
  ./start_service.sh
  2)启动所有机器上的监控脚本
   ./start_monitor.sh

6.停止
  ./stop_monitor.sh
  此时socket的服务端没有停，如果停止执行 ./stop_service.sh

7.重启
  修改config配置文件以后，进行重启
  执行./reboot_all_monitor.sh
