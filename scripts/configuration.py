import json
import os
import shutil
import setup_utils
import setup_non_priviliged
from print_colors import Color

print_color = Color()


def configure(data: dict, copy_data: dict, users: dict, dir: str):

    setup_utils.creat_missing_dirs()

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

    for k, v in copy_data.items():

        print(type(v))
        print(v)

        try:
            if os.path.isdir(f"{dir}{v.get('source')}"):

                for dst in v.get('destination'):
                    print(f"Destination: /mnt/archinstall{dst}")
                    shutil.copytree(f"{dir}{v.get('source')}",
                                    f"/mnt/archinstall{dst}", dirs_exist_ok=True)

            elif os.path.isfile(f"{dir}{v.get('source')}"):

                for dst in v.get('destination'):
                    print(f"Destination: /mnt/archinstall{dst}")
                    shutil.copyfile(f"{dir}{v.get('source')}",
                                    f"/mnt/archinstall{dst}")

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
