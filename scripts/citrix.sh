#!/bin/bash

export DEBIAN_FRONTEND="noninteractive"
debconf-set-selections <<<"icaclient app_protection/install_app_protection select no"
debconf-show icaclient
