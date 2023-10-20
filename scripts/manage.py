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
    root_directory = root_directory = os.path.realpath(
        os.path.dirname(__file__)).split("scripts")[0]
    script_directory = os.path.join(root_directory, "scripts")

    data_directory = os.path.join(root_directory, "data")
    download_directory = os.path.join(root_directory, "download")

    # Initialize parser
    parser = argparse.ArgumentParser(
        prog="DRK Ach Configurator",
        description="Configures the the Arch Linux, after the OS Installation.",
        epilog="Text at the bottom of help.",)

    # Adding optional argument
    parser.add_argument("-t", "--Type", action="store", required=True, type=str,
                        choices=["thin", "mobile", "mpg", "hnr"], help="Type of Device.",)

    parser.add_argument("-c", "--Configuration", action="store", required=True, type=str,
                        choices=["base", "mpg", "hnr"], help="Type of Configuration to be used.",)

    parser.add_argument("-hn", "--Hostname", action="store",
                        type=str, help="The hostname of the new system.")

    update_install = parser.add_mutually_exclusive_group(required=True)
    update_install.add_argument("-u", "--Update", action="store_true",
                                help="The Version you want to be installed.")
    update_install.add_argument("-i", "--Install", action="store_true",
                                help="The Version you want to be installed.")

    # Read arguments from command line
    args = parser.parse_args()

    match args.Type:
        case "thin":
            branch = "thin-client"
        case "mobile":
            branch = "mobile-client"
        case _:
            branch = "thin-client"

    match args.Configuration:
        case "hnr":
            config = "hnr"
        case "mpg":
            config = "mpg"
        case _:
            config = "base"

    if args.Hostname != None:
        hostname = args.Hostname
    else:
        hostname = f"drk-bs-{args.Type}-{args.Configuration}"

    # Merge and copy configuration files
    with open(f"{root_directory}/configs/base.json", "r") as f_base, open(
        f"{root_directory}/configs/{args.Configuration}.json", "r"
    ) as f_config, open(
        f"{root_directory}/type/{args.Type}/platform_config.json", "r"
    ) as f_platform_config, open(
        f"{root_directory}/configs/config.json", "w+"
    ) as f_merged:
        base_data = json.load(f_base)
        config_data = json.load(f_config)
        platform_config_data = json.load(f_platform_config)
        merged_data = utils.merge_and_update_dicts(base_data, config_data)
        merged_data = utils.merge_and_update_dicts(
            merged_data, platform_config_data)
        json.dump(merged_data, f_merged)

    # Get package, service and user data
    with open(f'{root_directory}/configs/config.json', 'r', encoding='utf-8') as f, open(f'{root_directory}/configs/copy.json', 'r', encoding='utf-8') as f2:
        file_content = json.load(f)
        copy_content = json.load(f2)
        installation_data = file_content['install']
        post_installation_data = file_content['post_install']
        users = file_content['users']
        f.close()

    # Start the linux installation
    if args.Install:
        if 'archiso' in socket.gethostname():
            print(socket.gethostname())
            parser.error(
                'You cannot reinstall if you are booted into a running system! Reboot to a USB-Drive and retry!')

        installation.install(data=installation_data,
                             users=users, hostname=hostname)

    elif args.Update:
        print('Update')
        setup_utils.sync_pacman()
    configuration.configure(data=post_installation_data,
                            copy_data=copy_content, users=users, dir=root_directory)

    # with open(f"{root_directory}/scripts/post_install.sh", 'r+') as f1, open(f'{root_directory}/type/{args.Type}/scripts/post_install.sh', 'r') as f2:
    #     f1.write(f2.read())
    # shutil.copyfile(f"{root_directory}/post_install.sh",
    #                 '/mnt/archinstall/home/admin/post.sh')
# Delete Downloaded git repo
# shutil.rmtree(os.path.realpath(
#     os.path.dirname(__file__)).split('scripts')[0])
