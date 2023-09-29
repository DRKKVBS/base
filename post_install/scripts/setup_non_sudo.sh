#! /bin/bash
cd /home/admin
pwd
git clone https://aur.archlinux.org/yay
cd yay/ && makepkg -si --noconfirm
cd ~ && rm -rf yay/
for pkg in "$@"; do
    yay -S $pkg --noconfirm
done
