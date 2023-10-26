import subprocess
import os
import shutil
import time
from print_colors import Color

print_color = Color()


def is_fresh_install():
    '''Check if the system is booted into the archiso.'''

    return not (os.path.ismount('/home') and os.path.ismount('/boot'))


def get_mount_path():
    if is_fresh_install():
        return '/mnt/archinstall'
    else:
        return '/'


def get_user_id(user: str):
    if user == 'admin':
        return 1000, 1000
    else:
        return 1001, 1001


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
    path = get_mount_path()
    print(path)

    uid, gid = get_user_id(user)

    for subpath in split_path(dir):
        path = os.path.normpath(os.path.join(path, subpath))
        if not os.path.exists(path):
            print_color.print_confirmation('Creating new direcotry: %s' % path)
            os.mkdir(path)
            shutil.chown(path, uid, gid)
            print_color.print_confirmation('Created directory: %s' % path)
        else:
            print_color.print_confirmation(
                'Directory already exists: %s' % path)
    time.sleep(5)


def add_desktop_app(file_path: str, user: str, visible_apps: list):
    path = get_mount_path()

    uid, gid = get_user_id(user)

    applications_path = os.path.join(path, '/home/', user,
                                     '.local/share/applications/')

    if not os.path.exists(applications_path):
        mkdirs_as_user(dir=path, user=user)

    app = os.path.split(file_path)[1]

    if os.path.exists(os.path.join(applications_path, app)):
        print_color.print_warning(
            'The file %s is already added to the %s' % (app, user))
        make_mutable(applications_path)
        return

    shutil.copyfile(
        file_path, os.path.join(applications_path, app))
    print(os.path.join(applications_path, app))
    shutil.chown(os.path.join(applications_path, app), uid, gid)

    if app in visible_apps:
        show_desktop_app(app, user)
    else:
        hide_desktop_app(app, user)

    make_immutable(applications_path)
    make_immutable(os.path.join(path, app))


def hide_desktop_app(app: str, user: str):
    '''Hide a desktop app from user so he cannot access via the acitvities screen.'''

    path = get_mount_path()

    if not os.path.exists(os.path.join(path, 'home', user, '.local', 'share', 'applications', app)):
        print_color.print_info(
            'The app %s is not accessible to %s' % (app, user))
        return
    make_mutable(os.path.join(path, 'home', user,
                 '.local', 'share', 'applications', app))
    with open(os.path.join(path, 'home', user, '.local', 'share', 'applications', app), "r+") as f:
        content = f.read()

        if "NoDisplay=true" in content:
            print_color.print_info(
                '%s is already hidden from %s' % (app, user))

        elif "NoDisplay=false" in content:
            content = content.replace(
                "NoDisplay=false", "NoDisplay=true")

        elif "NoDisplay" not in content:
            content = content.replace(
                "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=false")

        f.seek(0)
        f.truncate()
        f.write(content)

    make_immutable(os.path.join(path, 'home', user,
                   '.local', 'share', 'applications', app))


def show_desktop_app(app: str, user: str):
    '''Show a desktop app to user so he can access via the acitvities screen.'''
    path = get_mount_path()

    if not os.path.exists(os.path.join(path, 'home', user, '.local', 'share', 'applications', app)):
        print_color.print_info(
            'The app %s is not accessible to %s' % (app, user))
        return
    make_mutable(os.path.join(path, 'home', user,
                 '.local', 'share', 'applications', app))
    with open(os.path.join(path, 'home', user, '.local', 'share', 'applications', app), "r+") as f:
        content = f.read()

        if "NoDisplay=false" in content:
            print_color.print_info(
                '%s is already visible for %s' % (app, user))

        elif "NoDisplay=true" in content:
            content = content.replace(
                "NoDisplay=true", "NoDisplay=false")

        elif "NoDisplay" not in content:
            content = content.replace(
                "[Desktop Entry]", "[Desktop Entry]\nNoDisplay=true")

        f.seek(0)
        f.truncate()
        f.write(content)

    make_immutable(os.path.join(path, 'home', user,
                   '.local', 'share', 'applications', app))


def desktop_apps(desktop_app_dir: str, user: str, uid: int, gid: int, visible_apps: list):

    desktop_app_dir = os.path.normpath(desktop_app_dir)

    path = get_mount_path()

    print_color.print_info("STARTING: Setup Desktop Apps for %s" % user)

    make_mutable(f"/home/{user}/.local/share/applications/")
    for file in os.listdir(os.path.normpath(f"{path}/home/{user}/.local/share/applications/")):
        make_mutable(f"/home/{user}/.local/share/applications/{file}")
    # Copy the Desktop Files into the new directory
    shutil.copytree(
        desktop_app_dir, os.path.normpath(f"{path}/home/{user}/.local/share/applications/"), dirs_exist_ok=True)

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

    path = get_mount_path()

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
    path = get_mount_path()

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
    path = get_mount_path()

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
