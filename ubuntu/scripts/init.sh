#!/bin/bash

# Install packages
apt-get update
apt-get upgrade -y
apt-get install -y $(cat ../data/apt-requirements.txt)
apt purge -y gnome-initial-setup
pip3 install --upgrade pip
pip3 install -r ../data/pip-requirements.txt

python3 ./main.py

apt install -y displaylink-driver

dconf update
grub-mkconfig -o /boot/grub/grub.cfg
# reboot
