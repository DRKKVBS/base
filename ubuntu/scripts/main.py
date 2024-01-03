import argparse
import json
import os
import shutil
import utils

from user import User


def main():

    # Set the directory depending on the location of the script
    currrent_dir = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    data_dir = os.path.normpath(f"{currrent_dir}/data/")
    package_dir = os.path.normpath(f"{currrent_dir}/packages/")

    # Create missing directories
    for missing_dir in ["/etc/firefox/policies/", "/usr/share/icons/DRK/"]:
        os.makedirs(f"{missing_dir}", exist_ok=True)

    # Load the config file
    with open(f"{data_dir}/config.json", "r") as f:
        data = json.load(f)

    # Install packages from local directory
    if os.path.exists(package_dir):
        for pkg in os.listdir(package_dir):
            utils.install_package(
                pkg, os.path.normpath(f"{package_dir}/{pkg}"))

    # Create users
    users = []
    for _, user_data in data["users"].items():
        users.append(
            User(username=user_data["username"], password=user_data["password"], sudo=user_data["sudo"], desktop_entries=user_data["desktop"]))

    # Copy files
    for _, paths in data["files_to_copy"].items():
        shutil.copyfile(
            f"{data_dir}/{paths['source']}", f"{paths['destination']}")

    # Copy directories
    for _, paths in data["dirs_to_copy"].items():
        shutil.copytree(
            f"{data_dir}/{paths['source']}", f"{paths['destination']}", dirs_exist_ok=True)

    # Setup user specific configurations
    for user in users:

        # Copy custom desktop entries
        shutil.copytree(f"{data_dir}/DesktopEntries/",
                        os.path.normpath(f"{user.get_home_dir()}/.local/share/applications/"), dirs_exist_ok=True)

        # Set environment variables
        with open(os.path.normpath(f"{user.get_home_dir()}/.profile"), "a") as f:
            f.write("# Set environment variables\n")
            f.write(
                f"export DCONF_PROFILE={user.username}\n")

        for path in ["/var/lib/snapd/desktop/application/", "/usr/share/applications/"]:
            for app in os.listdir(path):
                if app.endswith(".desktop"):
                    shutil.copyfile(os.path.normpath(
                        f"/usr/share/applications/{app}"), os.path.normpath(f"{user.get_home_dir()}/.local/share/applications/{app}"))
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
            utils.set_file_permissions(
                f"/{user.get_home_dir()}/.local/share/applications/{file}", user.get_uid(), user.get_gid(), 0o664)


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
