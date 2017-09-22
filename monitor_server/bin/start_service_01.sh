#!/bin/bash
python ../lib/service.py  &
#tail -f ../log/monitor.log  | grep "`$time`" | ../lib/cronolog -k 7 ../log/oppf_esb_%Y%m%d.log &
#echo "python ../lib/service.py">startpy.sh
#sh startpy.sh >> ../log/nohup.log 2 >&1
