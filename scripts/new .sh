#!/bin/bash
git clone https://aur.archlinux.org/yay /home/admin/yay/
cd ./yay/
makepkg -si --noconfirm
cd ./
rm -rf ./yay/
