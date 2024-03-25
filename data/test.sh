#!/bin/bash

sudo apt install jq -y

echo '{"drk-logo": {"source": "/logos/drk-logo.png", "destination": "/usr/share/drk/drk-logo.png", "comment": "Logo for the login screen"}, "x11-vty-switch": {"source": "/01-vt-switch.conf","destination": "/etc/X11/xorg.conf.d/01-vt-switch.conf","comment": "Disable Virtual Terminals"}}' | jq '.drk-logo'