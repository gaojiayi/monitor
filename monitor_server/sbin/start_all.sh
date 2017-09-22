#!/bin/sh

APP_HOME="${HOME}/monitor_server/bin"

for file in `find $APP_HOME -name "start*.sh"|sort -r`
do
	cd `dirname $file`
	./`basename $file` > /dev/null 2>&1  &
	echo "${file}....................[ok]"
        sleep 5
done
