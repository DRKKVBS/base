#!/bin/bash




# Create missing dirs
sudo mkdir -p /etc/firefox/policies /usr/share/drk

# Create user
sudo useradd -m -s /bin/bash -G netdev Mitarbeiter 
sudo passwd -d Mitarbeiter
sudo -iu Mitarbeiter mkdir -pm 755 /home/Mitarbeiter/.config/ /home/Mitarbeiter/.local/share/applications

# Install packages
for pkg in "git" "gstreamer1.0-plugins-ugly" "python3-pip" "gnome-backgrounds" "vim" "dkms" "net-tools" "xfce4" "xfce4-goodies" "tightvncserver"; do
  sudo apt install $pkg -y
done 

# Remove unnecessary packages
for pkg in "gnome-initial-setup" "gnome-calender" "aisleriot" "cheese" "gnome-calculator" "gnome-characters" "libreoffice" "gnome-mahjongg" "gnome-mines" "seahorse" "remmina" "remmina-*" "rhythmbox" "shotwell" "gnome-sudoku" "gnome-todo" "totem" "gnome-video-effects"; do
  sudo apt remove $pkg -y
done 

# Update the system
sudo apt update && sudo apt upgrade -y

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

sudo tailscale up

echo "Lade das .deb Package für Citrix herunter. Es wird sich gleich Firefox öffen. Schließe das Fenster erst, sobald der Download abgeschlossen ist."
sleep 10
/snap/bin/firefox https://www.citrix.com/downloads/workspace-app/linux/workspace-app-for-linux-latest.html

export DEBIAN_FRONTEND="noninteractive"
sudo debconf-set-selections <<< "icaclient app_protection/install_app_protection select yes"
sudo debconf-show icaclient

# Install manually downloaded packages
search_dir=~/Downloads\
for entry in "$search_dir"/*
do
  sudo apt install $entry -y
done

sudo apt update

# Install Displaylink driver
sudo apt install displaylink-driver


# Download files
git clone https://github.com/drkkvbs/base /tmp/base

# Copy files
sudo python3 /tmp/base/scripts/main.py


# Upate Dconf database
sudo dconf update 
sudo grub-mkconfig -o /boot/grub/grub.cfg

# Setup Firefox



# Add devie to tailscale tenant
reboot
rm ~/base
