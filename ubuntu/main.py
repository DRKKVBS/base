import json
import os
import shutil
import utils

from user import User


def main():

    # Set the directory depending on the location of the script
    currrent_dir = os.path.realpath(
        os.path.dirname(__file__))  # TODO: Fix split()

    # Create missing dirs
    for missing_dir in ["/etc/firefox/policies/", "/usr/share/icons/DRK/"]:
        os.makedirs(f"{missing_dir}", exist_ok=True)

    # Load the config file
    with open(f"{currrent_dir}/config.json", "r") as f:
        data = json.load(f)
    print(type(data))

    users = []
    for user in data["users"]:
        print(type(user))
        print(user["username"])
        print(user["password"])
        print(user["sudo"])
        print(user["desktop"])
        users.append(
            User(username=user["username"], password=user["password"], sudo=user["sudo"], dekstop_entries=user["desktop"]))

    # Setup dconf
    shutil.copytree(os.path.normpath(f"/{currrent_dir}/dconf/"),
                    "/etc/dconf/", dirs_exist_ok=True)

    # Setup AccountsService
    shutil.copytree(os.path.normpath(f"/{currrent_dir}/AccountsService/"),
                    "/var/lib/AccountsService/", dirs_exist_ok=True)

    # Copy logo
    shutil.copyfile(os.path.normpath(
        f"/{currrent_dir}/logos/"), "/usr/share/icons/DRK/drk-logo.png")

    # Copy X11-Switch
    shutil.copyfile(os.path.normpath(
        f"/{currrent_dir}/01-vt-switch.conf"), "/etc/X11/xorg.conf.d/01-vt-switch.conf")

    # Copy Firefox autostart
    shutil.copyfile(os.path.normpath(
        f"/{currrent_dir}/myWorkspaceAutostart.desktop"), "/etc/xdg/autostart/myWorkspaceAutostart.desktop")

    # Setup user specific configurations
    for user in users:
        # Copy custom desktop entries
        shutil.copytree(f"/{currrent_dir}/DesktopEntries/",
                        os.path.normpath(f"{user.home_dir}/.local/share/applications/"), dirs_exist_ok=True)

        # Set environment variables
        with open(os.path.normpath(f"{user.home_dir}/.profile"), "a") as f:
            f.write("# Set environment variables\n")
            f.write(
                f"export DCONF_PROFILE={user.username}\n")

        # Set file permissions for desktop entries
        for file in os.listdir(os.path.normpath(f"/{user.home_dir}/.local/share/applications/")):
            utils.set_file_permissions(file, user.uid, user.gid, 0o664)

    # Copy systemd config drop ins
    shutil.copyfile(os.path.normpath(
        f"/{currrent_dir}/systemd/disable-vty.conf"), "/usr/lib/systemd/logind.conf.d/disable-vty.conf")
    shutil.copyfile(os.path.normpath(
        f"/{currrent_dir}/systemd/handle-lid-switch.conf"), "/usr/lib/systemd/logind.conf.d/handle-lid-switch.conf")


# def configure(data: dict, copy_data: dict, users: dict):

#     for _, v in copy_data.items():
#         setup_utils.copy_file(v)

#     for user, user_data in users.items():

#         for app in os.listdir("./general/data/DesktopEntries/"):

#             setup_utils.add_desktop_app(file_path=os.path.normpath(
#                 "./general/data/DesktopEntries/%s" % app), user=user, visible_apps=user_data['desktop'])

#         for app in os.listdir('/mnt/archinstall/usr/share/applications/'):
#             setup_utils.add_desktop_app(file_path=os.path.normpath(
#                 '/mnt/archinstall/usr/share/applications/%s' % app), user=user, visible_apps=user_data['desktop'])

#     for cmd in data["final_cmds"]:
#         setup_utils.run_command(cmd)


if __name__ == "__main__":
    main()
