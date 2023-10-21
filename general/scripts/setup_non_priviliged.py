import json
import os
import subprocess
import setup_utils
from print_colors import Color

print_color = Color()


def install_aur_package(chroot: bool, package: str):
    if chroot:
        pkgs = subprocess.run(["arch-chroot", "/mnt/archinstall/", "pacman", "-Qm"],
                       shell=False, capture_output=True, text=True).stdout
        if package not in pkgs:
            print_color.print_info('Installing %s' % package)
            setup_utils.arch_chroot_cmd(
                cmd=["yay", "-S", package, "--noconfirm"], uid=1000, gid=1000)
            print_color.print_confirmation('Installed %s successfull' % package)
        else:
            print_color.print_confirmation('%s is already installed' % package)

    else:
        
        pkgs = subprocess.run(["arch-chroot", "/mnt/archinstall/", "pacman", "-Qm"],
                       shell=False, capture_output=True, text=True).stdout
        if package not in pkgs:
            print_color.print_info('Installing %s' % package)
            setup_utils.arch_chroot_cmd(
                cmd=["yay", "-S", package, "--noconfirm"])
            print_color.print_confirmation('Installed %s successfull' % package)
        else:
            print_color.print_confirmation('%s is already installed' % package)
            


def install_yay():
    print_color.print_info('Installing yay')

    if not os.path.exists('/mnt/archinstall/usr/bin/yay'):
        subprocess.run("arch-chroot -u admin:admin /mnt/archinstall sudo -i -u admin /bin/bash -c 'git clone https://aur.archlinux.org/yay /home/admin/yay/; cd ./yay/ && makepkg -si --noconfirm; rm -rf /home/admin/yay/'",
                       shell=True)
        print_color.print_confirmation('Installed yay successfull')

    print_color.print_info(
        'Yay installation skipped! Yay is already installed!')


if __name__ == "__main__":
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split("scripts")[0]
