#!/bin/bash

systemctl stop post-install.service
systemctl disable post-install.service

userdel -r sebi

rm "$0"
