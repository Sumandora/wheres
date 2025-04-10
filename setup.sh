#!/bin/bash

WHERES=$(dirname "$0")

rm -rf $WHERES/venv

python -m venv $WHERES/venv
. $WHERES/venv/bin/activate
pip install -r $WHERES/requirements.txt
