#!/bin/sh

APP_HOME="${HOME}/monitor_node/bin"

for file in `find $APP_HOME -name "start*.sh"`
do
	cd `dirname $file`
	./`basename $file` > /dev/null 2>&1 &
	echo "${file}....................[ok]"
done
