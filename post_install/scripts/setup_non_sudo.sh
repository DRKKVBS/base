#! /bin/bash
git /home/admin clone https://aur.archlinux.org/yay
cd ./yay/ && makepkg -si --noconfirm
cd ./ && rm -rf ./yay/
for pkg in "$0"; do
    yay -S $pkg --noconfirm
done
