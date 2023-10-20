#!/usr/bin/env python

import json
import os
import argparse
import installation
import utils
import configuration
import setup_utils
import socket
from print_colors import Color


if __name__ == "__main__":

    print_color = Color()

    # Directories
    root_directory = '/tmp/base/'

    # Initialize parser
    parser = argparse.ArgumentParser(
        prog="DRK Ach Configurator",
        description="Configures the the Arch Linux, after the OS Installation.",
        epilog="Text at the bottom of help.",)

    # Adding optional argument
    parser.add_argument("-t", "--Type", action="store", required=True, type=str,
                        choices=["thin", "mobile"], help="Type of Device.",)

    parser.add_argument("-c", "--Configuration", action="store", required=True, type=str,
                        choices=["base", "usb"], help="Type of Configuration to be used.",)

    parser.add_argument("-hn", "--Hostname", action="store",
                        type=str, help="The hostname of the new system.")

    update_install = parser.add_mutually_exclusive_group(required=True)
    update_install.add_argument("-u", "--Update", action="store_true",
                                help="The Version you want to be installed.")
    update_install.add_argument("-i", "--Install", action="store_true",
                                help="The Version you want to be installed.")

    # Read arguments from command line
    args = parser.parse_args()

    if args.Hostname != None:
        hostname = args.Hostname
    else:
        hostname = f"drk-bs-{args.Type}-{args.Configuration}"

    # Merge and copy configuration files
    with open(os.path.normpath(f"{root_directory}/configs/base.json"), "r") as f_base, open(
        os.path.normpath(
            f"{root_directory}/configs/{args.Configuration}.json"), "r"
    ) as f_config, open(
        os.path.normpath(
            f"{root_directory}/configs/{args.Type}_config.json"), "r"
    ) as f_platform_config, open(
        os.path.normpath(f"{root_directory}/configs/config.json"), "w+"
    ) as f_merged:
        base_data = json.load(f_base)
        config_data = json.load(f_config)
        platform_config_data = json.load(f_platform_config)
        merged_data = utils.merge_and_update_dicts(base_data, config_data)
        merged_data = utils.merge_and_update_dicts(
            merged_data, platform_config_data)

        installation_data = merged_data['install']
        users = merged_data['users']
        post_installation_data = merged_data['post_install']

    with open(os.path.normpath(f"{root_directory}/configs/copy.json"), "r") as f_base, open(
        os.path.normpath(
            f"{root_directory}/configs/{args.Type}_copy.json"), "r"
    ) as f_platform:
        base_copy = json.load(f_base)
        platform_copy_data = json.load(f_platform)

        copy_merged = utils.merge_and_update_dicts(
            base_copy, platform_copy_data)

    # Start the linux installation
    if args.Install:
        if 'archiso' not in socket.gethostname():
            parser.error(
                'You cannot reinstall if you are booted into a running system! Reboot to a USB-Drive and retry!')
        else:
            installation.install(data=installation_data,
                                 users=users, hostname=hostname)

    elif args.Update:
        print('Update')
        setup_utils.sync_pacman()
    configuration.configure(data=post_installation_data,
                            copy_data=copy_merged, users=users, dir=root_directory)

    # with open(f"{root_directory}/scripts/post_install.sh", 'r+') as f1, open(f'{root_directory}/type/{args.Type}/scripts/post_install.sh', 'r') as f2:
    #     f1.write(f2.read())
    # shutil.copyfile(f"{root_directory}/post_install.sh",
    #                 '/mnt/archinstall/home/admin/post.sh')
# Delete Downloaded git repo
# shutil.rmtree(os.path.realpath(
#     os.path.dirname(__file__)).split('scripts')[0])
