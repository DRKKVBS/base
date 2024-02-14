#!/bin/bash

userdel -r drk

if test -f /etc/NetworkManager/system-connections/DRK_SAK_Mobile.nmconnection; then
    rm /etc/NetworkManager/system-connections/DRK_SAK_Mobile.nmconnection
fi

teamviewer --daemon start &

teamviewer assignment --id

rm "$0"

# systemctl enable displaylink
# systemctl start displaylink
