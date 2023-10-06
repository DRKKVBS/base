import json
import os
import shutil
import subprocess
import setup_utils
import setup_non_priviliged
from print_colors import Color

print_color = Color()


def configure(root_directory: str):
    with open(f"{root_directory}/configs/config.json", "r") as f:
        setup_json = json.load(f)
        post_install_json = setup_json["post_install"]

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

    try:
        for pkg in post_install_json["aur_pkgs"]:
            pass
            # setup_non_priviliged.install_aur_package(chroot=True, package=pkg)
    except:
        pass
    finally:
        setup_utils.reenable_sudo_password("admin")

    # setup_utils.dconf("%s/data/dconf/" % root_directory)

    # os.chmod('/home/admin/after_reboot.sh', mode=744)
    # subprocess.run(['/home/admin/after_reboot.sh'], shell=False)

    with open("/var/log/os", "w+") as f:
        f.write("Version 1.0")


if __name__ == "__main__":
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split("scripts")[0]
    configure(root_directory)
