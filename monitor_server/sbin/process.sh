#!/bin/sh

cd ..
rm -rf lib/*
cd lib
jar -xf ../ftpdir/monitor_server_lib.jar
rm -rf META-INF
cd ..
rm -rf config/*
cd config
jar -xf ../ftpdir/monitor_server_config.jar
rm -rf META-INF
#cd ..
#rm -rf configext/*
#cd configext
#jar -xf ../ftpdir/process_aicrm_exe_configext.jar
#rm -rf META-INF
cd ..
cd ftpdir
rm -rf *.jar
cd ../
echo success


