import json
import os
import shutil
import subprocess


def install_aur_package(chroot: bool, package: str):
    if chroot:
        subprocess.run(["arch-chroot", "-u", "admin:admin", "/mnt/archinstall", "yay", "-S", package, "--noconfirm"],
                       shell=False)

    else:
        subprocess.run(
            ["yay", "-S", package, "--noconfirm"],
            shell=False)


def install_yay():
    cmd = "{git clone https://aur.archlinux.org/yay /home/admin/yay/; cd ./yay/; makepkg -si --noconfirm; cd ./; rm -rf ./yay/}"
    subprocess.run("arch-chroot -u admin:admin /mnt/archinstall sudo -i -u admin /bin/bash << EOCHROOT\n pwd;\n whoami;\n EOCHROOT\n",
                   shell=True)


def setup(root_directory: str):
    with open(f"{root_directory}/config.json", "r") as f:
        setup_json = json.load(f)
        aur_pkgs = setup_json["post_install"]["aur_pkgs"]

    # Install yay
    print("Installing yay")
    subprocess.Popen(
        args="/usr/bin/git clone https://aur.archlinux.org/yay && cd yay/ && makepkg -si --noconfirm; cd && rm -rf yay/",
        group="admin",
        user="admin",
        shell=False,
        start_new_session=True)

    # Install third party packages
    for pkg in aur_pkgs:
        try:
            print(f"Installing {pkg}")
            subprocess.run(["yay", "-S", pkg, "--noconfirm"], shell=False)
        except Exception as e:
            print(
                f"AN ERROR OCCURED! {str(pkg).upper()} COULD NOT BE INSTALLED!")
            print(e)
        else:
            print(f"Installation of {pkg} was succesfull")


if __name__ == "__main__":
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split("scripts")[0]
    setup(root_directory)
