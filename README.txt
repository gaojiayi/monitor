��飺

	��Ⱥ��Ӧ�����еĽ���״̬���ݶ�ʱ�ɼ���أ�����ǰ̨չʾ���͸澯������Ҫ���ESB��Seda��GC������Ѵ�С��mongodb���ڴ�ʹ�ã�redis�ڴ�ʹ�������redis����ʹ��Ƶ��ʹ��shell�������ݲɼ�����python���͵�����ˡ��������Ҫ���߳̽��մ������ݣ��������ʷ����oracle��⣬�������ݵ�redis��⡣����ʵʱ���������־����������ͳһ���ù�����ͣ����ȹ��ܡ�


����װ��

1.�������迪��SSH��SFTP����
2.�����˰�װ��
  1��cx_oracle
   $rpm -ivh cx_Oracle-5.1.2-11g-py27-1.x86_64.rpm 
   $ls /usr/lib/python2.7/site-packages/cx_Oracle.so #������ļ���ʾ��װ�ɹ�,����python��װλ�õ���ǰ�˲��֡�
  2��oracle�ͻ���  ������գ�http://www.tbdazhe.com/archives/602
   $unzip basic-11.1.0.70-linux-x86_64.zip
   $cd instantclient_11_1
   $cp * /usr/lib   #ֱ�ӷŵ���̬������·���У�����Ҫ����Ļ�������
   ��
   $unzip basic-11.1.0.70-linux-x86_64.zip
   $cp -rf instantclient_11_1 /opt/
   $vi /etc/profile
      export ORACLE_HOME=/opt/instantclient_11_1
����  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME
 
   $source /etc/profile
  3��redisģ��
    tar -zvxf redis-2.8.0.tar.gz
    mv redis-2.8.0 python-redis-2.8.0
    cd python-redis-2.8.0
    python setup.py install
  4��paramikoģ�飨�Ȱ�װ PyCrypto�� ������գ�http://www.cnblogs.com/xia520pi/p/3805043.html
    tar -zxvf pycrypto-2.6.tar.gz
    cd pycrypto-2.6/
    python setup.py build && python setup.py install

    tar xvzf paramiko-1.7.7.1.tar.gz
    cd paramiko-1.7.7.1/
    python setup.py build && python setup.py install
   
   5��Pexpectģ�鰲װ
    tar xzf pexpect-2.3.tar.gz
    cd pexpect-2.3
    sudo python ./setup.py install
    
   6)��װpooledDB���ӳ�ģ��
     tar -zxvf DBUtils-1.1.tar
     cd DBUtils-1.1
     python setup.py install
   7)��װthreadpoolģ��
     tar -jxvf  threadpool-1.3.2.tar.bz2
     cd threadpool-1.3.2/
     python setup.py install

3.�ű����� ���ڼ�ػ����ϣ���ͬ��Ŀ¼�·���monitor_service�ļ����ڵ����нű�����monitor_node�����Ϸ��������ļ����ڵ����нű���
                 

4.�����ű�ǰ���ã�
  config.xml ������oracle����Դ��redis���ӣ����˽ű�Ŀ¼����ض˽ű�Ŀ¼��socket�˿ڣ���ض��û���Ϣ�ͷ�����û���Ϣ���Լ�����ض��������ʱ�䡣
  
  monitor_stat.sh  ������jdk��mongodb��redis�İ�װbinĿ¼��

5.����
  1)����socket�����
   cd bin 
  ./start_service.sh
  2)�������л����ϵļ�ؽű�
   ./start_monitor.sh

6.ֹͣ
  ./stop_monitor.sh
  ��ʱsocket�ķ����û��ͣ�����ִֹͣ�� ./stop_service.sh

7.����
  �޸�config�����ļ��Ժ󣬽�������
  ִ��./reboot_all_monitor.sh
