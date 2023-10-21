import socket
import subprocess
import os
import shutil
from print_colors import Color

print_color = Color()


def is_fresh_install():
    '''Check if the system is booted into the archiso.'''

    return os.path.ismount('/home') and os.path.ismount('/boot')


def run_command(cmd: list, uid=None, gid=None):
    '''Run commands in the arch-chroot environment.'''

    if is_fresh_install:
        if uid is None or gid is None:
            subprocess.run(["arch-chroot", "/mnt/archinstall/", *cmd],
                           shell=False)
        else:
            subprocess.run(["arch-chroot", "-u", "%d:%d" % (uid or gid, gid or uid), "/mnt/archinstall/", *cmd],
                           shell=False)
    else:
        subprocess.run([*cmd],
                       shell=False)


def split_path(path: str):
    '''Split a path into its sub paths.'''

    sub_directories = []
    while 1:
        path, sub = os.path.split(path)
        if sub != "":
            sub_directories.append(sub)
        else:
            if path != "":
                sub_directories.append(path)
            break

    return list(reversed(sub_directories))


def mkdirs_as_user(dir: str, user="root"):
    '''Create new directories and set the owner as the specified user.'''

    dir = os.path.normpath(dir)
    if is_fresh_install():
        path = '/mnt/archinstall/'
    else:
        path = '/'
    for subpath in split_path(dir):
        path = os.path.join(path, subpath)
        if not os.path.exists(path):
            print_color.print_confirmation('Creating new direcotry: %s' % path)
            os.mkdir(path)
            shutil.chown(path, user, user)
        else:
            print_color.print_confirmation(
                'Directory already exists: %s' % path)


def desktop_apps(desktop_app_dirs: str, user: str, uid: int, gid: int, visible_apps: list):

    desktop_app_dirs = os.path.normpath(desktop_app_dirs)

    if is_fresh_install:
        path = "/mnt/archinstall/"
    else:
        path = "/"

    print_color.print_info("STARTING: Setup Desktop Apps for %s" % user)

    make_mutable(f"/home/{user}/.local/share/applications/")
    for file in os.listdir(os.path.normpath(f"{path}/home/{user}/.local/share/applications/")):
        make_mutable(f"/home/{user}/.local/share/applications/{file}")
    # Copy the Desktop Files into the new directory
    shutil.copytree(
        desktop_app_dirs, os.path.normpath(f"{path}/home/{user}/.local/share/applications/"), dirs_exist_ok=True)

    # Make Desktop Entries hidden
    for file in os.listdir(os.path.normpath(f"{path}/usr/share/applications/")):
        if os.path.islink(os.path.normpath(f"{path}/usr/share/applications/{file}")):
            continue
        shutil.copyfile(os.path.normpath(f"{path}/usr/share/applications/{file}"),
                        os.path.normpath(f"{path}/home/{user}/.local/share/applications/{file}"))
    for file in os.listdir(os.path.normpath(f"{path}/home/{user}/.local/share/applications/")):
        shutil.chown(
            os.path.normpath(f"{path}/home/{user}/.local/share/applications/{file}"), user=uid, group=gid)
        with open(f"{path}/home/{user}/.local/share/applications/{file}", "r+") as f2:
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
        make_immutable(f"/home/{user}/.local/share/applications/{file}")
    # Make the directory immutable
    make_immutable(f"/home/{user}/.local/share/applications/")


def make_immutable(path: str):
    '''Make a file or a directory immutable using Chattr.'''

    path = os.path.normpath(path)
    run_command(["chattr", "+i", path])


def make_mutable(path: str):
    '''Make a file or a directory mutable using Chattr.'''

    path = os.path.normpath(path)
    run_command(["chattr", "-i", path])


def sync_pacman():
    '''Sync the pacman database.'''

    run_command(['pacman', '-Syy'])


def enable_group_for_sudo(group: str):

    if is_fresh_install:
        path = "/mnt/archinstall"
    else:
        path = "/"

    print_color.print_info_critical(
        "Enabling group for sudo for %s" % (group))
    try:
        shutil.copyfile('/tmp/base/security/00_wheel',
                        f'{path}/etc/sudoers.d/00_wheel')
        print_color.print_info_critical(
            "Enabled group for sudo for %s" % (group))
    except Exception as e:
        print_color.print_error(
            "ERROR: Enabling group for sudo for %s failed! | %s" % (group, e))
        pass


def disable_sudo_password(user: str):
    if is_fresh_install:
        path = "/mnt/archinstall/"
    else:
        path = "/"

    print_color.print_info_critical(
        "STARTING: Disable sudo password for %s" % (user))
    try:
        shutil.copyfile('/tmp/base/security/01_admin',
                        f'{path}/etc/sudoers.d/01_admin')
        print_color.print_info_critical(
            "SUCCESSFUL: Disabled sudo password for %s" % (user))
    except Exception as e:
        print_color.print_error(
            "ERROR: Disabling sudo password for %s failed! | %s" % (user, e))
        pass


def reenable_sudo_password(user: str):
    if is_fresh_install:
        path = '/mnt/archinstall/'
    else:
        path = '/'

    print_color.print_info_critical(
        'STARTING: Reenable sudo password for %s' % (user))
    try:
        os.remove(f'{path}/etc/sudoers.d/01_admin')
        print_color.print_info_critical(
            "SUCCESSFUL: Reenabled sudo password for %s" % (user))
    except Exception as e:
        print_color.print_error(
            "ERROR: Reenabling sudo password for %s failed! | %s" % (user, e))


if __name__ == "__main__":
    root_dir = os.path.realpath(os.path.dirname(__file__)).split("scripts")[0]
