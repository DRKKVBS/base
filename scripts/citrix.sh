#!/bin/bash

export DEBIAN_FRONTEND="noninteractive"
sudo debconf-set-selections <<<"icaclient app_protection/install_app_protection select yes"
sudo debconf-show icaclient
