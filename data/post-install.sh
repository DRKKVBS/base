#!/bin/bash

CLONE_DIR="/tmp/base"

# Create missing dirs
echo "Create missing directories"
sudo mkdir -p /etc/firefox/policies /usr/share/drk

# Update the system
sudo apt update && sudo apt upgrade -y

# Install packages
echo "Install missing packages"
for pkg in "jq" "git" "gstreamer1.0-plugins-ugly" "python3-pip" "gnome-backgrounds" "vim" "dkms" "net-tools" "xfce4" "xfce4-goodies" "tightvncserver" "language-pack-de" "language-pack-gnome-de"; do
    sudo apt install $pkg -y
done

# Remove unnecessary packages
echo "Remove unused packages"
for pkg in "gnome-initial-setup" "gnome-calender" "aisleriot" "cheese" "gnome-calculator" "gnome-characters" "libreoffice" "gnome-mahjongg" "gnome-mines" "seahorse" "remmina" "remmina-*" "rhythmbox" "shotwell" "gnome-sudoku" "gnome-todo" "totem" "gnome-video-effects"; do
    sudo apt autoremove $pkg -y
done

# Update the system
sudo apt update && sudo apt upgrade -y

# Download files
echo "Download files from GitHub"
git clone https://github.com/drkkvbs/base $CLONE_DIR

# Set German as default Language
sudo update-locale LANG=de_DE.UTF-8 LANGUAGE=de_DE

# Download Citrix
echo "Lade das .deb Package für Citrix herunter. Es wird sich gleich Firefox öffen. Schließe das Fenster erst, sobald der Download abgeschlossen ist."

/snap/bin/firefox https://www.citrix.com/downloads/workspace-app/linux/workspace-app-for-linux-latest.html

# Create user
echo "Hinzufügen des Mitarbeiter Accounts"
sudo useradd -m -s /bin/bash -G netdev Mitarbeiter
sudo passwd -d Mitarbeiter
sudo -iu Mitarbeiter mkdir -pm 755 /home/Mitarbeiter/.config/ /home/Mitarbeiter/.local/share/applications

# Collect User Data for later use
declare -A arr_user=(["id"]=$(id -u Mitarbeiter) ["gid"]=$(id -g Mitarbeiter) ["home"]="/home/Mitarbeiter")
declare -A arr_admin=(["id"]=$(id -u Administrator) ["gid"]=$(id -g Administrator) ["home"]="/home/Administrator")

# User specific configurations
for arr in "${!arr_@}"; do

    declare -n users_arr="$arr"

    # Set wfica client as default application for .ica files
    # Citrix Workspace opens automatically when a .ica file is downloaded
    echo "Füge x-ica zu den MimeApps"
    sudo echo "[Added Associations]\napplication/x-ica=wfica.desktop" >>"${users_arr[home]}"/.config/mimeapps.list

    # Set environment variable
    echo "Setzte Umgebunsvariable"
    sudo echo "# Set environment variables\nexport DCONF_PROFILE={user.username}\n" >>"${users_arr[home]}"/.profile

    # Copy custom desktop entries
    echo "Kopiere custom DesktopEntries"
    sudo cp $CLONE_DIR/DesktopEntries/* "${users_arr[home]}"/.local/share/applications/

    # Copy all Desktop Entries
    echo "Kopiere Desktop Apps"
    for app_dir in "/var/lib/snapd/desktop/applications" "/usr/share/applications"; do
        ls $app_dir | grep .desktop | while read -r line; do
            sudo cp "$app_dir/$line" "${users_arr[home]}"/.local/share/applications/
        done
    done

    # Only display desktop entries mentioned in....
    echo "No Display"
    for user_application in $(ls "${users_arr[home]}"/.local/share/applications/); do
        if [ $(find $(cat $CLONE_DIR/user_home.txt) $user_application) ]; then
            if [ $(find "${users_arr[home]}"/.local/share/applications/$user_application "NoDisplay=True") ]; then
                sed -i 's/NoDisplay=True/NoDisplay=False/g' "${users_arr[home]}"/.local/share/applications/$user_application
            else
                sed -i 's/[Destop Entry]/[Destop Entry]\nNoDisplay=False/g' "${users_arr[home]}"/.local/share/applications/$user_application
            fi
        else
            if [ $(find "${users_arr[home]}"/.local/share/applications/$user_application "NoDisplay=Fasle") ]; then
                sed -i 's/NoDisplay=False/NoDisplay=True/g' "${users_arr[home]}"/.local/share/applications/$user_application
            else
                sed -i 's/[Destop Entry]/[Destop Entry]\nNoDisplay=True/g' "${users_arr[home]}"/.local/share/applications/$user_application
            fi
        fi

        # Set Ownership
        sudo chown root:"${users_arr[gid]}" $user_application

        # Set Permissions
        sudo chmod 755 $user_application
    done

done

# Download and install displaylink
wget https://www.synaptics.com/sites/default/files/Ubuntu/pool/stable/main/all/synaptics-repository-keyring.deb -O ~/Downloads/synaptics-repository-keyring.deb && sudo apt install ~/Downloads/synaptics-repository-keyring.deb -y && sudo apt update

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Connect Client to Tailscale Account
sudo tailscale up --auth-key tskey-auth-kTWtjQA6g421CNTRL-y5JT4kjLxFC8bnz2eYTpFChn6Y5vwgNk

# Non interactive option for Citrix app protection
export DEBIAN_FRONTEND="noninteractive"
sudo debconf-set-selections <<<"icaclient app_protection/install_app_protection select yes"
sudo debconf-show icaclient

# Install Citrix
CITRIX=$(ls ~/Downloads | grep icaclient)
sudo apt install ~/Downloads/$CITRIX -y

sudo apt update

# Copy files
# sudo python3 /tmp/base/scripts/main.py

# Upate Dconf database
sudo dconf update
sudo grub-mkconfig -o /boot/grub/grub.cfg

# Setup Firefox

rm -r $CLONE_DIR

# Install Displaylink driver
sudo apt install displaylink-driver -y

# Add devie to tailscale tenant
reboot
