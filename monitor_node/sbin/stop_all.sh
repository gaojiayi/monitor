#!/bin/sh

APP_HOME="${HOME}/monitor_node/bin"

for file in `find $APP_HOME -name "stop*.sh"`
do
	cd `dirname $file`
	fname=`basename $file`
	msg=`./$fname`
	echo "${file}...............[${msg}]"
done
