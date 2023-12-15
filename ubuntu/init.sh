#!/bin/bash

# Install packages
apt-get update
apt-get upgrade -y
apt-get install -y $(cat apt-requirements.txt)
pip3 install --upgrade pip
pip3 install -r pip-requirements.txt

python3 ./main.py
