#!/bin/bash

# Install packages
search_dir=../packages/
for entry in "$search_dir"*; do
    apt install -y $entry
done
apt-get update
apt-get install -y $(cat ../data/apt-requirements.txt)
apt-get upgrade -y
apt purge -y gnome-initial-setup
pip3 install --upgrade pip
pip3 install -r ../data/pip-requirements.txt

python3 ./main.py

apt update

apt install -y displaylink-driver

dconf update
grub-mkconfig -o /boot/grub/grub.cfg

# reboot
