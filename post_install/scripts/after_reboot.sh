#! /bin/bash
systemctl enable displaylink
systemctl start displaylink
systemctl enable teamviewerd
teamviewer daemon --start
