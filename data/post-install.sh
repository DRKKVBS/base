#!/bin/bash

# Delete the default user
sudo userdel -r drk

# Delete the public wifi connection
if test -f /etc/NetworkManager/system-connections/DRK_SAK_Mobile.nmconnection; then
    sudo rm /etc/NetworkManager/system-connections/DRK_SAK_Mobile.nmconnection
fi

# Start Teamviewer
sudo teamviewer --daemon start
teamviewer &

sleep 15

# Assign the device to the account
sudo teamviewer assignment --id

# Delete the script
sudo rm "$0"
