#!/bin/bash

sudo python3 ~/base/scripts/main.py

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

sudo tailscale up

echo "Lade das .deb Package für Citrix herunter. Es wird sich gleich Firefox öffen. Schließe das Fenster erst, sobald der Download abgeschlossen ist."
sleep 10
/snap/bin/firefox https://www.citrix.com/downloads/workspace-app/linux/workspace-app-for-linux-latest.html

export DEBIAN_FRONTEND="noninteractive"
sudo debconf-set-selections <<< "icaclient app_protection/install_app_protection select yes"
sudo debconf-show icaclient

CITRIX="$(ls ~/Downloads/ | grep 'icaclient')"
sudo apt install -f ~/Downloads/$CITRIX -y

# Add devie to tailscale tenant

rm ~/base
