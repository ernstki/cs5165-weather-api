#!/bin/sh
export FLASK_APP=weatherapi/api.py

cd /deploy
source venv/bin/activate
flask run --host=0.0.0.0
