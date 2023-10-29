#!/usr/bin/env python

import json
import os
import argparse
import shutil
import installation
import utils
import configuration
import setup_utils
from print_colors import Color
import logging

print_color = Color()

logging.basicConfig(filename='/tmp/base/logs/example.log',
                    encoding='utf-8', level=logging.DEBUG)


if __name__ == "__main__":

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

    # Merge and copy configuration files
    with open("./configs/general_config.json", "r") as f_base, open(
        os.path.normpath(
            f"./configs/{args.Configuration}_config.json"), "r"
    ) as f_config, open(
        os.path.normpath(
            f"./configs/{args.Type}_config.json"), "r"
    ) as f_platform_config:
        base_data = json.load(f_base)
        config_data = json.load(f_config)
        platform_config_data = json.load(f_platform_config)
        merged_config_data = utils.merge_and_update_dicts(
            base_data, config_data)
        merged_config_data = utils.merge_and_update_dicts(
            merged_config_data, platform_config_data)

        installation_data = merged_config_data['install']
        users = merged_config_data['users']
        post_installation_data = merged_config_data['post_install']

    with open("./configs/general_copy.json", "r") as f_base, open(
        os.path.normpath(
            f"./configs/{args.Type}_copy.json"), "r"
    ) as f_platform:
        base_copy = json.load(f_base)
        platform_copy_data = json.load(f_platform)

        copy_merged = utils.merge_and_update_dicts(
            base_copy, platform_copy_data)

    # Start the linux installation
    if args.Install:

        if setup_utils.is_fresh_install():
            parser.error(
                "You cannot reinstall if you are booted into a running system! Reboot to a USB-Drive and retry!")
        else:
            installation.install(data=installation_data,
                                 users=users, hostname=hostname)

    elif args.Update:
        setup_utils.sync_pacman()
    configuration.configure(data=post_installation_data,
                            copy_data=copy_merged, users=users)

    # Add type specific post_install commands to post_install scripts
    with open("./general/scripts/post_install.sh", "r+") as f_gen, open(f"{root_directory}/type/{args.Type}/scripts/post_install.sh", "r") as f_type:
        f_gen.write(f_type.read())
    shutil.copyfile("./general/scripts/post_install.sh",
                    "/mnt/archinstall/home/admin/post.sh")

    # Save config files for later debugging and updating
    os.mkdir("/mnt/archinstall/var/log/drk")
    shutil.copytree("./logs/", "/mnt/archinstall/var/log/drk")
    with open("/mnt/archinstall/var/log/drk/" "a") as f:
        json.dump(merged_config_data, f)


# Delete Downloaded git repo
# shutil.rmtree(os.path.realpath(
#     os.path.dirname(__file__)).split("scripts")[0])
