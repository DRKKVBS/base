#!/bin/bash

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Add devie to tailscale tenant

# Delete the default user
userdel -r drk

# Delete the script
rm "$0"
