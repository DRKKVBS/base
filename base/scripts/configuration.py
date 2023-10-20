import json
import os
import shutil
import setup_utils
import setup_non_priviliged
from print_colors import Color

print_color = Color()


def configure(data: dict, copy_data: dict, users: dict, dir: str):
    dir = os.path.normpath(dir)

    # Create missing user specific directories
    for user in ['admin', 'user']:
        for missing_dir in [f'/home/{user}/.config/environment.d/', f'/home/{user}/.local/share/applications/']:
            setup_utils.mkdirs_as_user(user, os.path.normpath(missing_dir))

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
        for pkg in data["aur_pkgs"]:
            setup_non_priviliged.install_aur_package(chroot=True, package=pkg)
    except:
        pass
    finally:
        setup_utils.reenable_sudo_password("admin")

    for _, v in copy_data.items():
        try:
            source = os.path.normpath(f"{dir}{v.get('source')}")
            destination = os.path.normpath(
                f"/mnt/archinstall{v.get('destination')}")
            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
            elif os.path.isfile(source):
                shutil.copyfile(source, destination)
            if v.get('permissions'):
                os.chown(destination, uid=v.get(
                    'permissions').get('uid'), gid=v.get('permissions').get('gid'))

        except Exception as e:
            print(e)
            pass

    for user, data in users.items():
        if user == 'admin':
            gid = uid = 1000
        else:
            gid = uid = 1001
        setup_utils.desktop_apps("%s/data/DesktopEntries/" %
                                 dir, user, gid, uid, data['desktop'])
    setup_utils.final_commands()
    setup_utils.enable_group_for_sudo('wheel')

    # with open("/var/log/os", "a") as f:
    #     f.write("Version 1.0")


if __name__ == "__main__":
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split("scripts")[0]
