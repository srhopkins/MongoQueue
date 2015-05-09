#!/bin/bash

/opt/mongo*/bin/mongod --smallfiles --quiet --logpath /dev/null &

[ -f /notebooks/requirements.txt ] && pip install -r /notebooks/requirements.txt

ipython notebook --no-browser --ip=* --port 8888
