#!/bin/bash

userdel -r sebi
rm /etc/systemc/system/post-install.service
rm "$0"
