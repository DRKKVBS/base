import subprocess
import os
import shutil
from print_colors import Color
import logging

print_color = Color()


def req():
    os.chdir("/tmp/base/")


def is_fresh_install():
    '''Check if the system is booted into the archiso.'''

    return not (os.path.ismount("/home") and os.path.ismount("/boot"))


def get_mount_point():
    '''Return the current mount point.'''

    if is_fresh_install():
        return "/mnt/archinstall/"
    else:
        return "/"


def get_uid(user: str):

    path = get_mount_point()

    with open(os.path.normpath("%s/etc/passwd" % path), "r") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith(user):
            return int(line.split(":")[2])
    else:
        raise ValueError("User '%s' does not exist!" % user)



def copy_file(data: dict):

    if is_fresh_install:
        path = "/mnt/archinstall/"
    else:
        path = "/"

    source = os.path.normpath(f"../{data['source']}")
    destination = os.path.normpath(
        f"{path}/{data['destination']}")
    if os.path.isdir(source):
        try:
            shutil.copytree(source, destination, dirs_exist_ok=True)
        except FileExistsError as e:
            logging.error("The file already exists %s" % e)

        except Exception as e:
            logging.error("error %s" % e)

    else:
        try:
            shutil.copyfile(source, destination)
        except Exception as e:
            logging.error("Failed to copy the file %s! %s" %
                          (data.get('source'), e))

        if data.get('permissions'):
            shutil.chown(
                path=destination, user=data['permissions']['uid'], group=data['permissions']['gid'])


def get_gid(group: str):
    path = get_mount_point()

    with open(os.path.normpath("%s/etc/passwd" % path), "r") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith(group):
            return int(line.split(":")[2])
    else:
        raise ValueError("Group '%s' does not exist!" % group)


def run_command(cmd: list, uid=None, gid=None):
    '''Run commands in the arch-chroot environment.'''

    if is_fresh_install:
        if uid is None or gid is None:
            cmd_list = ["arch-chroot", "/mnt/archinstall/", *cmd]

        else:
            cmd_list = ["arch-chroot", "-u", "%d:%d" %
                        (uid or gid, gid or uid), "/mnt/archinstall/", *cmd]
    else:
        cmd_list = [*cmd]

    try:
        logging.info("Execute command: %s" % cmd_list)
        r = subprocess.run([*cmd_list], shell=False)
        return r
    except Exception as e:
        logging.error("Failed to execute command: ", cmd_list, e)


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
    path = get_mount_point()

    try:
        uid = get_uid(user)
        gid = get_gid(user)

    except ValueError as e:
        print(e)
        logging.error(e)
        return

    for subpath in split_path(dir):
        path = os.path.normpath(f'{path}/{subpath}')
        if not os.path.exists(path):
            logging.info("Creating new direcotry: %s" % path)
            os.mkdir(path)
            logging.info("Setting Ownership to uid: %s, gid: %s" % (uid, gid))
            shutil.chown(path, uid, gid)
        else:
            logging.warn("Directory already exists: %s" % path)


def add_desktop_app(file_path: str, user: str, visible_apps: list):
    path = get_mount_point()

    try:
        uid = get_uid(user)
        gid = get_gid(user)

    except ValueError as e:
        logging.error(e)
        return

    applications_path = os.path.normpath(
        "%s/home/%s/.local/share/applications/" % (path, user))

    if not os.path.exists(applications_path):
        mkdirs_as_user(dir=path, user=user)

    make_mutable(os.path.normpath(
        "/home/%s/.local/share/applications/" % user))

    app = os.path.split(file_path)[1]

    if os.path.exists(os.path.normpath(f'{applications_path}/{app}')):
        print_color.print_warning(
            "The file %s is already added to the %s" % (app, user))
        make_immutable(os.path.normpath(
            "/home/%s/.local/share/applications/" % user))
        return

    shutil.copyfile(
        file_path, os.path.normpath(f'{applications_path}/{app}'))
    print(os.path.normpath(f'{applications_path}/{app}'), uid, gid)
    shutil.chown(os.path.normpath(f'{applications_path}/{app}'), uid, gid)

    if app in visible_apps:
        show_desktop_app(app, user)
    else:
        hide_desktop_app(app, user)

    make_immutable(os.path.normpath(
        "/home/%s/.local/share/applications/" % user))
    make_immutable(os.path.normpath(
        f"/home/{user}/.local/share/applications/{app}"))


def hide_desktop_app(app: str, user: str):
    '''Hide a desktop app from user so he cannot access via the acitvities screen.'''

    path = get_mount_point()

    if not os.path.exists(os.path.normpath("%s/home/%s/.local/share/applications/%s" % (path, user, app))):
        print_color.print_info(
            "The app %s is not accessible to %s" % (app, user))
        return
    make_mutable(os.path.normpath(
        "/home/%s/.local/share/applications/%s" % (user, app)))
    with open(os.path.normpath(
            "%s/home/%s/.local/share/applications/%s" % (path, user, app)), "r+") as f:
        content = f.read()

        if "NoDisplay=true" in content:
            print_color.print_info(
                "%s is already hidden from %s" % (app, user))

        elif "NoDisplay=false" in content:
            content = content.replace(
                "NoDisplay=false", "NoDisplay=true")

        elif "NoDisplay" not in content:
            content = content.replace(
                "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=true")

        f.seek(0)
        f.truncate()
        f.write(content)

    make_immutable(os.path.normpath(
        "/home/%s/.local/share/applications/%s" % (user, app)))


def show_desktop_app(app: str, user: str):
    '''Show a desktop app to user so he can access via the acitvities screen.'''
    path = get_mount_point()

    if not os.path.exists(os.path.normpath(
            "%s/home/%s/.local/share/applications/%s" % (path, user, app))):
        print_color.print_info(
            "The app %s is not accessible to %s" % (app, user))
        return
    make_mutable(os.path.normpath(
        "/home/%s/.local/share/applications/%s" % (user, app)))
    with open(os.path.normpath(
            "%s/home/%s/.local/share/applications/%s" % (path, user, app)), "r+") as f:
        content = f.read()

        if "NoDisplay=false" in content:
            print_color.print_info(
                "%s is already visible for %s" % (app, user))

        elif "NoDisplay=true" in content:
            content = content.replace(
                "NoDisplay=true", "NoDisplay=false")

        elif "NoDisplay" not in content:
            content = content.replace(
                "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=false")

        f.seek(0)
        f.truncate()
        f.write(content)

    make_immutable(os.path.normpath(
        "/home/%s/.local/share/applications/%s" % (user, app)))


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

    path = get_mount_point()

    logging.fatal("Enabling group for sudo for %s" % (group))
    try:
        shutil.copyfile('/tmp/base/security/00_wheel',
                        f'{path}/etc/sudoers.d/00_wheel')
        logging.fatal("Enabled group for sudo for %s" % (group))
    except shutil.SameFileError as e:
        logging.error(
            "The source file and the destination file are identical! | %s" % e)

    except Exception as e:
        logging.error(
            "Enabling group for sudo for %s failed! | %s" % (group, e))


def disable_sudo_password(user: str):
    path = get_mount_point()

    logging.fatal("Disabling sudo password for %s" % (user))
    try:
        shutil.copyfile("/tmp/base/security/01_admin",
                        f"{path}/etc/sudoers.d/01_admin")
        logging.fatal("Disabled sudo password for %s" % (user))
    except Exception as e:
        logging.error(
            "Disabling sudo password for %s failed! | %s" % (user, e))


def reenable_sudo_password(user: str):
    path = get_mount_point()

    logging.warning("Reenabling sudo password for %s" % (user))
    try:
        os.remove(f"{path}/etc/sudoers.d/01_admin")
        logging.fatal("Reenabled sudo password for %s" % (user))
    except Exception as e:
        logging.error(
            "Reenabling sudo password for %s failed! | %s" % (user, e))


def already_installed(package: str):
    '''Check if the package is already installed on the running system.'''

    if is_fresh_install():
        r = subprocess.run(["arch-chroot", "/mnt/archinstall/", "pacman", "-Qs", package],
                           shell=False, capture_output=True, text=True).stdout

    else:
        r = subprocess.run(["pacman", "-Qs", package],
                           shell=False, capture_output=True, text=True).stdout

    return False if r == "b''" else True


def install_aur_package(package: str):
    '''Install an aur package to the system.'''

    disable_sudo_password("admin")

    already_installed(package)

    if is_fresh_install():

        if not already_installed(package):
            logging.info("Installing %s" % package)
            try:
                run_command(
                    cmd=["yay", "-S", package, "--noconfirm"], uid=1000, gid=1000)

                logging.debug("Installed %s" % package)
            except Exception as e:
                logging.error("Failed to install ", package, e)
            finally:
                reenable_sudo_password("admin")
        else:
            logging.info("%s is already installed" % package)

    else:
        if not already_installed(package):
            logging.info("Installing %s" % package)

            try:
                run_command(
                    cmd=["yay", "-S", package, "--noconfirm"])
                logging.debug("Installed %s" % package)
            except Exception as e:
                logging.error("Failed to install ", package, e)
            finally:
                reenable_sudo_password("admin")

        else:
            logging.info(
                "%s is already installed" % package)


def install_yay():

    disable_sudo_password("admin")

    if os.path.exists("/mnt/archinstall/usr/bin/yay"):
        logging.debug(
            "Yay installation skipped! Yay is already installed!")
        return
    logging.info("Installing Yay")
    try:
        subprocess.run("arch-chroot -u admin:admin /mnt/archinstall sudo -i -u admin /bin/bash -c 'git clone https://aur.archlinux.org/yay /home/admin/yay/; cd ./yay/ && makepkg -si --noconfirm; rm -rf /home/admin/yay/'",
                       shell=True)
    except Exception as e:
        logging.error("Installation of Yay failed! ", e)

    finally:
        reenable_sudo_password("admin")

    logging.debug("Installed Yay")


if __name__ == "__main__":
    root_dir = os.path.realpath(os.path.dirname(__file__)).split("scripts")[0]
