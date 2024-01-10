#!/bin/bash

# Install packages
apt update
apt upgrade
search_dir=../packages/
for entry in "$search_dir"*; do
    apt install -y $entry
done

apt update

apt install -y $(cat ../data/apt-requirements.txt)
apt upgrade -y
apt purge -y gnome-initial-setup
pip3 install --upgrade pip
pip3 install -r ../data/pip-requirements.txt

python3 ./main.py

dconf update
grub-mkconfig -o /boot/grub/grub.cfg

reboot
