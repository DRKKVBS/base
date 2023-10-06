import json
import subprocess
import os
import shutil
import setup_priviliged_type
from print_colors import Color
import utils

print_color = Color()


def setup(root_directory: str):
    # Update dconf db, remove user from "wheel" group, change user password, create correct timezone, update grub config
    for cmd in [
        ["dconf", "update"],
        ["usermod", "-G", "user", "user"],
        ["passwd", "-d", "user"],
        ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"],
    ]:
        subprocess.run(cmd, shell=False)


def logos(logo_dir: str):
    print_color.print_info("STARTING: Copy Logos to new System")
    # Copy Logos
    shutil.copytree(logo_dir, "/usr/share/logos/", dirs_exist_ok=True)
    print_color.print_confirmation("SUCCESSFUL: Copied Logos to new System")


def icons(icon_dir: str):
    print_color.print_info("STARTING: Copy Icons to new System")
    # Copy Logos
    shutil.copytree(icon_dir, "/var/lib/AccountsService/icons",
                    dirs_exist_ok=True)
    print_color.print_confirmation("SUCCESSFUL: Copied Icons to new System")


def grub(grub_file: str):
    print_color.print_info("STARTING: Grup Setup")
    try:
        with open("/mnt/archinstall/etc/default/grub", "w+") as f, open(grub_file, "r") as f1:
            f.write(f1.read())
        print_color.print_confirmation("SUCCESSFUL: Grup Setup")
    except Exception as e:
        print_color.print_error("ERROR: Grub Setup failed! | %s" % (e))
        pass


def gdm(gdm_file: str):
    print_color.print_info("STARTING: GDM Setup")
    try:
        with open("/mnt/archinstall/etc/gdm/custom.conf", "w+") as f, open(gdm_file, "r") as f1:
            f.write(f1.read())
            print_color.print_confirmation("SUCCESSFUL: GDM Setup")
    except Exception as e:
        print_color.print_error("ERROR: Grub Setup failed! | %s" % (e))
        pass


def dconf(dconf_dir: str):
    print_color.print_info("STARTING: Dconf Setup")
    shutil.copytree(dconf_dir, "/mnt/archinstall/etc/dconf/",
                    dirs_exist_ok=True)
    print_color.print_confirmation("SUCCESSFUL: Dconf Setup")


def environment_variable(variable_name: str, variable_value: str, user: str):
    if user is "admin":
        uid = gid = 1000
    else:
        uid = gid = 1001
    print_color.print_info(
        "STARTING: Creating Environment variable %s=%s"
        % (variable_name, variable_value)
    )
    os.makedirs(
        f"/mnt/archinstall/home/{user}/.config/environment.d/", exist_ok=True)
    os.chown(f"/mnt/archinstall/home/{user}/.config/", uid=uid, gid=gid)
    os.chown(
        f"/mnt/archinstall/home/{user}/.config/environment.d", uid=uid, gid=gid)
    try:
        with open(
            f"/mnt/archinstall/home/{user}/.config/environment.d/variables.conf", "w+"
        ) as f:
            f.write(f"{variable_name}={variable_value}\n")
            print_color.print_confirmation("SUCCESSFUL: GDM Setup")
        make_immutable(
            f"/mnt/archinstall/home/{user}/.config/environment.d/variables.conf"
        )
    except Exception as e:
        print_color.print_error(
            "ERROR: Creation Environment variable %s=%s failed! | %s"
            % (variable_name, variable_value, e)
        )

        pass


def desktop_apps(
    desktop_app_dirs: str, user: str, uid: int, gid: int, visible_apps: list
):
    # Create Directories if they do not exist
    if not os.path.exists(f"/mnt/archinstall/home/{user}/.local/share/applications/"):
        os.makedirs(
            f"/mnt/archinstall/home/{user}/.local/share/applications/", exist_ok=True
        )
        os.chown(f"/mnt/archinstall/home/{user}/.local/", uid=uid, gid=gid)
        os.chown(
            f"/mnt/archinstall/home/{user}/.local/share/", uid=uid, gid=gid)
        os.chown(
            f"/mnt/archinstall/home/{user}/.local/share/applications/", uid=uid, gid=gid)

    # Copy the Desktop Files into the new directory
    shutil.copytree(
        desktop_app_dirs, "/mnt/archinstall/home/%s/.local/share/applications/" % user, dirs_exist_ok=True
    )

    # Make Dekstop Entries hidden
    for file in os.listdir("/mnt/archinstall/usr/share/applications/"):
        content = ""
        if os.path.exists(
            f"/mnt/archinstall/home/{user}/.local/share/applications/{file}"
        ):
            make_file_mutubale(
                f"/mnt/archinstall/home/{user}/.local/share/applications/{file}"
            )
        with open(f"/mnt/archinstall/usr/share/applications/{file}", "r") as f1:
            content = f1.read()
            if "NoDisplay=true" in content:
                continue
        shutil.copyfile(
            f"/mnt/archinstall/usr/share/applications/{file}",
            f"/home/{user}/.local/share/applications/{file}",
        )
        with open(
            f"/mnt/archinstall/home/{user}/.local/share/applications/{file}", "w"
        ) as f2:
            if "NoDisplay=false" in content and file not in visible_apps:
                content = content.replace("NoDisplay=false", "NoDisplay=true")
            elif file not in visible_apps:
                content = content.replace(
                    "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=true"
                )
            f2.write(content)
        # Make File immutable
        make_immutable(
            f"/mnt/archinstall/home/{user}/.local/share/applications/{file}")
    # Make the directory immutable
    make_immutable(f"/mnt/archinstall/home/{user}/.local/share/applications/")


def make_immutable(path: str):
    subprocess.run(
        ["chattr", "+i", path],
        shell=False,
    )


def make_file_mutubale(path: str):
    subprocess.run(
        ["chattr", "-i", path],
        shell=False,
    )


def accountsservices(accs_dir: str):
    print_color.print_info("STARTING: Copy AccountsService to new System")
    shutil.copytree(accs_dir, "/mnt/archinstall/etc/dconf/",
                    dirs_exist_ok=True)
    print_color.print_confirmation(
        "SUCCESSFUL: Copied AccountsService to new System")


def disable_sudo_password(user: str):
    print_color.print_info_critical(
        "STARTING: Disable sudo password for %s" % (user))
    try:
        with open("/mnt/archinstall/etc/sudoers.d/00_admin", "w+") as f:
            f.write("%s ALL=(ALL) NOPASSWD: ALL" % (user))
        print_color.print_info_critical(
            "SUCCESSFUL: Disabled sudo password for %s" % (user)
        )
    except Exception as e:
        print_color.print_error(
            "ERROR: Disabling sudo password for %s failed! | %s" % (user, e)
        )
        pass


def reenable_sudo_password(user: str):
    print_color.print_info_critical(
        "STARTING: Reenable sudo password for %s" % (user))
    try:
        os.remove("/mnt/archinstall/etc/sudoers.d/00_admin")
        print_color.print_info_critical(
            "SUCCESSFUL: Reenabled sudo password for %s" % (user)
        )
    except Exception as e:
        print_color.print_error(
            "ERROR: Reenabling sudo password for %s failed! | %s" % (user, e)
        )
        pass


def firefox(root_directory: str):
    print_color.print_info("STARTED: Setting up Firefox")
    # Firefox
    if not os.path.exists("/mnt/archinstall/usr/share/firefox/"):
        os.makedirs("/mnt/archinstall/usr/share/firefox/", exist_ok=True)
        print_color.print_info(
            "Created new Direcotries: /mnt/archinstall/usr/share/firefox/"
        )

    shutil.copytree(
        f"{root_directory}/data/firefox/", "/mnt/archinstall/usr/share/firefox/"
    )
    if not os.path.exists("/etc/firefox/policies/"):
        os.makedirs("/etc/firefox/policies/", exist_ok=True)
        print_color.print_info(
            "Created new Direcotries: /etc/firefox/policies/")
    shutil.copyfile(
        f"{root_directory}/data/firefox/policies.json",
        "/etc/firefox/policies/policies.json",
    )
    print_color.print_confirmation("SUCCESSFUL: Setting up Firefox")


def wifi(wifi_dir: str):
    print_color.print_info("STARTING: Set IWD as Wifi-Backend")
    shutil.copyfile(wifi_dir, "/etc/NetworkManager/conf.d/wifi_backend.conf")
    print_color.print_confirmation("SUCCESSFUL: Set IWD as Wifi-Backend")


def autostart(autostart_dir: str):
    # Setup Autostart apps
    print_color.print_info("STARTING: Setup Autostart Apps")
    shutil.copyfile(
        autostart_dir, "/etc/xdg/autostart/myWorkspaceAutostart.desktop")
    print_color.print_confirmation("SUCCESSFUL: Setup Autostart Apps")


if __name__ == "__main__":
    root_dir = os.path.realpath(os.path.dirname(__file__)).split("scripts")[0]
    setup(root_dir)
