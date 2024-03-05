import json
import os
import shutil
import subprocess


from custom_logger import logger
from user import User
from utils import fs_helper, pkg_helper, helper


def main():

    root = fs_helper.get_root_dir()

    # Load the config file
    try:
        with open(f"{root}/configs/config.json", "r") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        exit(1)

    if data['workplace'] == None:
        data['workplace'] = helper.input_validation(
            "Please enter the workplace the employee. bs or rhf...\n")
        logger.info(f"Worplace set to {data['workplace']}")

    if data['client_num'] == None:
        data['client_num'] = helper.input_validation(
            "Please enter a Number...\n")
        logger.info(f"client_num set to {data['client_num']}")

    # Set a new hostname
    helper.set_hostname(f"sak-{data['workplace']}-{data['client_num']}")

    if data["users"]["admin"]["password"] == None:
        data["users"]["admin"]["password"] = helper.input_validation(
            "Please enter a password for the Administrator account and press enter to continue...")
        logger.info(
            f"Administrator password set to {data['users']['admin']['password']}")

    pkg_helper.update_package_db()

    # Remove packages
    for pkg in data["packages"]["remove"]:
        pkg_helper.remove_package(pkg)

    # Make icaclient installation non interactive
    os.environ["DEBIAN_FRONTEND"] = "noninteractive"
    subprocess.run(["debconf-set-selections"], shell=True, check=True,
                   input=b"icaclient app_protection/install_app_protection select yes\n")
    subprocess.run(["debconf-show", "icaclient"], check=True)

    # Install packages from the packages directory
    for pkg in os.listdir(os.path.normpath(f"{root}/packages/")):
        pkg_helper.install_file(os.path.normpath(f"{root}/packages/{pkg}"))

    pkg_helper.update_package_db()

    # Install packages
    for pkg in data["packages"]["install"]:
        pkg_helper.install_package(pkg)

    pkg_helper.update_package_db()
    pkg_helper.upgrade_pkgs()

    # Install pip packages
    for cmd in [["pip3", "install", "--upgrade", "pip"],
                ["pip3", "install", "-r", "../configs/pip-requirements.txt"]]:
        subprocess.run(cmd, check=True)

    # Create missing directories
    # Needed to copy files later on
    for missing_dir in ["/etc/firefox/policies/", "/usr/share/drk/"]:
        try:
            logger.info(f"Creating directory {missing_dir}")
            os.makedirs(f"{missing_dir}", exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directory {missing_dir}: {e}")

    # Create users
    users = []
    for _, user_data in data["users"].items():
        users.append(
            User(username=user_data["username"], password=user_data["password"], sudo=user_data["sudo"], desktop_entries=user_data["desktop"]))

    # Copy files
    for _, paths in data["files_to_copy"].items():
        try:
            shutil.copyfile(os.path.normpath(
                f"{root}/data/{paths['source']}"), f"{paths['destination']}")
        except Exception as e:
            logger.error(f"Error copying file: {e}")

    # Copy directories
    for _, paths in data["dirs_to_copy"].items():
        try:
            shutil.copytree(os.path.normpath(
                f"{root}/data/{paths['source']}"), f"{paths['destination']}", dirs_exist_ok=True)
        except Exception as e:
            logger.error(f"Error copying directory: {e}")

    # Setup user specific configurations
    for user in users:

        # Copy custom desktop entries
        shutil.copytree(os.path.normpath(f"{root}/data//DesktopEntries/"),
                        os.path.normpath(f"{user.get_home_dir()}/.local/share/applications/"), dirs_exist_ok=True)

        # Set environment variables
        with open(os.path.normpath(f"{user.get_home_dir()}/.profile"), "a+") as f:
            f.write("# Set environment variables\n")
            f.write(
                f"export DCONF_PROFILE={user.username}\n")

        # Set wfica client as default application for .ica files
        # Citrix Workspace opens automatically when a .ica file is downloaded
        with open(os.path.normpath(f"{user.get_home_dir()}/.config/mimeapps.list"), "a+") as f:
            f.write(
                "[Added Associations]\napplication/x-ica=wfica.desktop")

        for path in ["/var/lib/snapd/desktop/applications/", "/usr/share/applications/"]:
            for app in os.listdir(path):
                if app.endswith(".desktop"):
                    shutil.copyfile(os.path.normpath(
                        f"{path}/{app}"), os.path.normpath(f"{user.get_home_dir()}/.local/share/applications/{app}"))
                    with open(os.path.normpath(f"{user.get_home_dir()}/.local/share/applications/{app}"), "r+") as f:
                        content = f.read()
                        if app in user.desktop_entries:
                            if "NoDisplay=true" in content:
                                content = content.replace(
                                    "NoDisplay=true", "NoDisplay=false")
                            elif "NoDisplay=false" not in content:
                                content = content.replace(
                                    "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=false")
                        else:
                            if "NoDisplay=false" in content:
                                content = content.replace(
                                    "NoDisplay=false", "NoDisplay=true")
                            elif "NoDisplay=true" not in content:
                                content = content.replace(
                                    "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=true")
                        f.seek(0)
                        f.truncate()
                        f.write(content)

        # Set file permissions for desktop entries
        for file in os.listdir(os.path.normpath(f"/{user.get_home_dir()}/.local/share/applications/")):
            fs_helper.set_file_permissions(
                f"/{user.get_home_dir()}/.local/share/applications/{file}", user.get_uid(), user.get_gid(), 0o664)

    # Set file permissions
    os.chmod("/home/admin/post-install.sh", 0o111)

    for cmd in [["dconf", "update"], ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], ["reboot"]]:
        subprocess.run(cmd, check=True)


if __name__ == "__main__":

    # # Initialize parser
    # parser = argparse.ArgumentParser(
    #     prog="DRK Ubuntu Configurator",
    #     description="Configures the the Ubuntu Linux, after the OS Installation.",
    #     epilog="Placeholder.",)

    # # Adding optional argument
    # parser.add_argument("-t", "--Type", action="store", required=True, type=str,
    #                     choices=["thin", "mobile"], help="Type of Device.",)

    # parser.add_argument("-c", "--Configuration", action="store", required=True, type=str,
    #                     choices=["base", "usb"], help="Type of Configuration to be used.",)

    # parser.add_argument("-hn", "--Hostname", action="store",
    #                     type=str, help="The hostname of the new system.")

    # # Read arguments from command line
    # args = parser.parse_args()

    # if args.Hostname != None:
    #     hostname = args.Hostname
    # else:
    #     hostname = f"drk-bs-{args.Type}-{args.Configuration}"

    main()
    # utils.test()
