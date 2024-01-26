#!/bin/bash

userdel -r drk
rm /etc/NetworkManager/system-connections/DRK_SAK_Mobile.nmconnection

rm "$0"

# systemctl enable displaylink
# systemctl start displaylink
# systemctl enable teamviewer
# teamviewer --daemon start
