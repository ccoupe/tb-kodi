#!/bin/bash
node=`hostname`
nm-online
cd /usr/local/lib/kodi-track
source PYENV/bin/activate
python3 tbkodi.py -c ${node}.json
