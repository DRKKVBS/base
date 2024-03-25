#!/bin/bash

sudo apt install jq -y

echo '{"drk-logo": {"source": "/logos/drk-logo.png", "destination": "/usr/share/drk/drk-logo.png", "comment": "Logo for the login screen"}}' | jq '.drk-logo'