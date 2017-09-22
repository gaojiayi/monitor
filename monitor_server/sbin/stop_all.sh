#!/bin/sh

APP_HOME="${HOME}/monitor_server/bin"

for file in `find $APP_HOME -name "stop*.sh"`
do
	cd `dirname $file`
	fname=`basename $file`
	msg=`./$fname`
	echo "${file}...............[ok]"
done
