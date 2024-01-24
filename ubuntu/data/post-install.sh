#!/bin/bash

userdel -r drk
rm /etc/NetworkManager/system-connections/DRK_SAK_Mobile.nmconnection

rm "$0"
