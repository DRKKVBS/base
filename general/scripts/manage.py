#!/usr/bin/env python

import json
import os
import argparse
import shutil
import setup_utils
import logging


if __name__ == "__main__":

    logging.basicConfig(filename='./logs/example.log',
                        encoding='utf-8', level=logging.DEBUG)

    # Directories
    root_directory = "/tmp/base/"

    # Initialize parser
    parser = argparse.ArgumentParser(
        prog="DRK Arch Installer",
        description="Configures the the Arch Linux, after the OS Installation.",
        epilog="Placeholder.",)

    # Adding optional argument
    parser.add_argument("-t", "--Type", action="store", required=True, type=str,
                        choices=["thin", "mobile"], help="Type of Device.",)

    parser.add_argument("-c", "--Configuration", action="store", required=True, type=str,
                        choices=["base", "usb"], help="Type of Configuration to be used.",)

    parser.add_argument("-hn", "--Hostname", action="store",
                        type=str, help="The hostname of the new system.")

    update_install = parser.add_mutually_exclusive_group(required=True)
    update_install.add_argument("-u", "--Update", action="store_true",
                                help="Update the system configuration.")
    update_install.add_argument("-i", "--Install", action="store_true",
                                help="Install a new Image.")

    # Read arguments from command line
    args = parser.parse_args()

    if args.Hostname != None:
        hostname = args.Hostname
    else:
        hostname = f"drk-bs-{args.Type}-{args.Configuration}"
