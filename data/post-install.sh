#!/bin/bash

# Delete the default user
userdel -r drk

# Delete the public wifi connection
if test -f /etc/NetworkManager/system-connections/DRK_SAK_Mobile.nmconnection; then
    rm /etc/NetworkManager/system-connections/DRK_SAK_Mobile.nmconnection
fi

# Start Teamviewer
teamviewer --daemon start
teamviewer &

# Assign the device to the account
teamviewer assignment --id

# Delete the script
rm "$0"
