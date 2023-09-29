#! /bin/bash
pwd | sudo -i -u admin 
env
git -C /home/admin clone https://aur.archlinux.org/yay
cd ./yay/ && makepkg -si --noconfirm
cd ./ && rm -rf ./yay/
for pkg in "$@"; do
    yay -S $pkg --noconfirm
done
