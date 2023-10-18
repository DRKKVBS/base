!#/usr/bin/python

import json
import os
import shutil
import subprocess
import setup_utils
import setup_non_priviliged
from print_colors import Color

print_color = Color()


def configure(root_directory: str):
    with open(f"{root_directory}/config.json", "r") as f:
        setup_json = json.load(f)
        post_install_json = setup_json["post_install"]
        users = setup_json['users']

    setup_utils.disable_sudo_password("admin")
    try:
        setup_non_priviliged.install_yay()
    except Exception as e:
        print_color.print_error(
            "ERROR: Installation of yay failed! | %s"
            % (e)
        )
    finally:
        setup_utils.reenable_sudo_password("admin")

    setup_utils.disable_sudo_password("admin")
    try:
        for pkg in post_install_json["aur_pkgs"]:
            setup_non_priviliged.install_aur_package(chroot=True, package=pkg)
    except:
        pass
    finally:
        setup_utils.reenable_sudo_password("admin")

    with open(f"{root_directory}/data/copy.json", "r") as f:
        data = json.load(f)
        for k, v in data.items():
            try:
                if os.path.isdir(f"{root_directory}/data/{v.get('source')}"):
                    shutil.copytree(f"{root_directory}/data/{v.get('source')}",
                                    f"/mnt/archinstall/{v.get('destination')}")
                elif os.path.isfile(f"{root_directory}/data/{v.get('source')}"):
                    shutil.copyfile(f"{root_directory}/data/{v.get('source')}",
                                    f"/mnt/archinstall/{v.get('destination')}")
            except Exception as e:
                pass

    for user, data in users.items():
        if user == 'admin':
            gid = uid = 1000
        else:
            gid = uid = 1001
        for var, value in data['environment_variables'].items():
            setup_utils.environment_variable(
                variable_name=var, variable_value=value, user=user, gid=gid, uid=uid)
        for app in data['desktop']:
            setup_utils.desktop_apps("%s/data/DesktopEntries/" %
                                     root_directory, user, gid, uid, app)
    setup_utils.final_commands()
    setup_utils.enable_group_for_sudo('wheel')

    # with open("/var/log/os", "a") as f:
    #     f.write("Version 1.0")


if __name__ == "__main__":
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split("scripts")[0]
    configure(root_directory)

    
