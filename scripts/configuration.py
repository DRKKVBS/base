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

    setup_utils.dconf("%s/data/dconf/" % root_directory)
    setup_utils.logos("%s/data/images/logos/" % root_directory)
    setup_utils.icons("%s/data/images/icons/" % root_directory)
    setup_utils.grub("%s/data/grub" % root_directory)
    setup_utils.gdm("%s/data/gdm.conf" % root_directory)
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
    setup_utils.accountsservices("%s/data/AccountsService/" % root_directory)
    setup_utils.firefox("%s/data/firefox/" % root_directory)
    setup_utils.wifi("%s/data/wifi/wifi_backend.conf" % root_directory)
    setup_utils.autostart("%s/data/autostart/" % root_directory)
    setup_utils.final_commands()
    setup_utils.enable_group_for_sudo('wheel')

    with open("/var/log/os", "w+") as f:
        f.write("Version 1.0")


if __name__ == "__main__":
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split("scripts")[0]
    configure(root_directory)
