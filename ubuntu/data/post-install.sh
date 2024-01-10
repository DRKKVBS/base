#!/bin/bash

systemctl stop post-install.service
systemctl disable post-install.service

userdel -r sebi
rm /etc/systemc/system/post-install.service
rm "$0"
