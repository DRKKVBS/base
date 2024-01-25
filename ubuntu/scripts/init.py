import json
import utils
import os
import main


root_dir = utils.get_root_dir()

utils.run_command(["apt", "update"])
utils.run_command(["snap", "remove", "--purge", "firefox"])
utils.run_command(["apt", "upgrade", "-y"])

# Install packages from the packages directory
for pkg in os.listdir(os.path.normpath(f"{root_dir}/packages/")):
    utils.install_package(pkg)

utils.run_command(["apt", "update"])

# Install packages from the packages directory
with open(os.path.normpath(f"{root_dir}/script_configs/config.json")) as f:
    pkgs = json.load(f)
    for pkg in pkgs["apt_packages"]:
        utils.install_package(pkg)

utils.run_command(["apt", "update"])
utils.run_command(["apt", "upgrade", "-y"])

utils.run_command(["apt", "purge", "-y", "gnome-initial-setup"])
utils.run_command(["pip3", "install", "--upgrade", "pip"])
utils.run_command(["pip3", "install", "-r", "../data/pip-requirements.txt"])

main.main()
utils.run_command(["dconf", "update"])
utils.run_command(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])
# utils.run_command(["reboot"])
