import subprocess
import os
import shutil
from print_colors import Color

print_color = Color()


def run_command_arch_chroot(cmd: list, uid=None, gid=None):
    if uid is None or gid is None:
        subprocess.run(["arch-chroot", "/mnt/archinstall/", *cmd],
                       shell=False)
    else:
        subprocess.run(["arch-chroot", "-u", "%d:%d" % (uid or gid, gid or uid), "/mnt/archinstall/", *cmd],
                       shell=False)


def final_commands():
    ''''''
    # Update dconf db, remove user from "wheel" group, change user password, create correct timezone, update grub config
    cmds = [
        ["dconf", "update"],
        ["usermod", "-G", "user", "user"],
        ["passwd", "-d", "user"],
        ["passwd", "-l", "root"],
        ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"]
    ]
    for cmd in cmds:
        run_command_arch_chroot(cmd)


def desktop_apps(desktop_app_dirs: str, user: str, uid: int, gid: int, visible_apps: list):
    print_color.print_info("STARTING: Setup Desktop Apps for %s" % user)
    # Create Directories if they do not exist
    if not os.path.exists(f"/mnt/archinstall/home/{user}/.local/share/applications/"):
        print_color.print_info("    Creating new Directories %s" % user)
        os.makedirs(
            f"/mnt/archinstall/home/{user}/.local/share/applications/", exist_ok=True)
        os.chown(f"/mnt/archinstall/home/{user}/.local/", uid=uid, gid=gid)
        os.chown(
            f"/mnt/archinstall/home/{user}/.local/share/", uid=uid, gid=gid)
        os.chown(
            f"/mnt/archinstall/home/{user}/.local/share/applications/", uid=uid, gid=gid)

    make_mutable(f"/home/{user}/.local/share/applications/")
    for file in os.listdir(f"/mnt/archinstall/home/{user}/.local/share/applications/"):
        make_mutable(
            f"/home/{user}/.local/share/applications/{file}")
    # Copy the Desktop Files into the new directory
    shutil.copytree(
        desktop_app_dirs, "/mnt/archinstall/home/%s/.local/share/applications/" % user, dirs_exist_ok=True)

    # Make Desktop Entries hidden
    for file in os.listdir("/mnt/archinstall/usr/share/applications/"):
        if os.path.islink(f"/mnt/archinstall/usr/share/applications/{file}"):
            continue
        shutil.copyfile(f"/mnt/archinstall/usr/share/applications/{file}",
                        f"/mnt/archinstall/home/{user}/.local/share/applications/{file}")
    for file in os.listdir(f"/mnt/archinstall/home/{user}/.local/share/applications/"):
        os.chown(
            f"/mnt/archinstall/home/{user}/.local/share/applications/{file}", uid=uid, gid=gid)
        with open(f"/mnt/archinstall/home/{user}/.local/share/applications/{file}", "r+") as f2:
            content = f2.read()
            if "NoDisplay=false" in content and file not in visible_apps:
                content = content.replace("NoDisplay=false", "NoDisplay=true")
            elif file not in visible_apps:
                content = content.replace(
                    "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=true")
            f2.seek(0)
            f2.truncate()
            f2.write(content)
            # Make File immutable
        make_immutable(
            f"/home/{user}/.local/share/applications/{file}")
    # Make the directory immutable
    make_immutable(f"/home/{user}/.local/share/applications/")


def make_immutable(path: str):
    run_command_arch_chroot(["chattr", "+i", path])


def make_mutable(path: str):
    run_command_arch_chroot(["chattr", "-i", path])


def sync_pacman():
    run_command_arch_chroot(['pacman', '-Syy'])


def enable_group_for_sudo(group: str):
    print_color.print_info_critical(
        "STARTING: Enabling group for sudo for %s" % (group))
    try:
        with open("/mnt/archinstall/etc/sudoers.d/00_%s" % group, "w+") as f:
            f.write("%%%s ALL=(ALL) ALL" % (group))
        print_color.print_info_critical(
            "SUCCESSFUL: Enabled group for sudo for %s" % (group))
    except Exception as e:
        print_color.print_error(
            "ERROR: Enabling group for sudo for %s failed! | %s" % (group, e))
        pass


def disable_sudo_password(user: str):
    print_color.print_info_critical(
        "STARTING: Disable sudo password for %s" % (user))
    try:
        with open("/mnt/archinstall/etc/sudoers.d/00_admin", "w+") as f:
            f.write("%s ALL=(ALL) NOPASSWD: ALL" % (user))
        print_color.print_info_critical(
            "SUCCESSFUL: Disabled sudo password for %s" % (user))
    except Exception as e:
        print_color.print_error(
            "ERROR: Disabling sudo password for %s failed! | %s" % (user, e))
        pass


def reenable_sudo_password(user: str):
    print_color.print_info_critical(
        "STARTING: Reenable sudo password for %s" % (user))
    try:
        os.remove("/mnt/archinstall/etc/sudoers.d/00_admin")
        print_color.print_info_critical(
            "SUCCESSFUL: Reenabled sudo password for %s" % (user))
    except Exception as e:
        print_color.print_error(
            "ERROR: Reenabling sudo password for %s failed! | %s" % (user, e))


def firefox(firefox_dir: str):
    print_color.print_info("STARTED: Setting up Firefox")
    # Firefox
    if not os.path.exists("/mnt/archinstall/usr/share/firefox/"):
        os.makedirs("/mnt/archinstall/usr/share/firefox/", exist_ok=True)
        print_color.print_info(
            "Created new Direcotries: /mnt/archinstall/usr/share/firefox/")

    shutil.copytree(
        f"{firefox_dir}share/", "/mnt/archinstall/usr/share/firefox/", dirs_exist_ok=True)
    if not os.path.exists("/mnt/archinstall/etc/firefox/policies/"):
        os.makedirs("/mnt/archinstall/etc/firefox/policies/", exist_ok=True)
        print_color.print_info(
            "Created new Direcotries: /etc/firefox/policies/")
    shutil.copyfile(
        f"{firefox_dir}policies.json",
        "/mnt/archinstall/etc/firefox/policies/policies.json")
    print_color.print_confirmation("SUCCESSFUL: Setting up Firefox")


if __name__ == "__main__":
    root_dir = os.path.realpath(os.path.dirname(__file__)).split("scripts")[0]
    setup(root_dir)
