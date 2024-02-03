#!/bin/bash
# Make the Citrix Receiver installation non-interactive.
# To disable the app protection feature, set the "app_protection/install_app_protection select no" Otherwise replace "no" with "yes".
export DEBIAN_FRONTEND="noninteractive"
debconf-set-selections <<<"icaclient app_protection/install_app_protection select no"
debconf-show icaclient
