#!/bin/bash

which python3.13 >/dev/null 2>&1 || { echo "Python 3.13 is required"; exit; }

WHERES=$(dirname "$0")

rm -rf $WHERES/venv

python3.13 -m venv $WHERES/venv
. $WHERES/venv/bin/activate
pip install -r $WHERES/requirements.txt
