#!/bin/bash
systemctl enable displaylink
systemctl start displaylink
systemctl enable teamviewer
teamviewer --daemon start