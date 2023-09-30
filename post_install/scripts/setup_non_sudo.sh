#! /bin/bash
git clone https://aur.archlinux.org/yay /home/admin
cd ./yay/ && makepkg -si --noconfirm
cd ./ && rm -rf ./yay/
for pkg in "$@"; do
    yay -S $pkg --noconfirm
done
