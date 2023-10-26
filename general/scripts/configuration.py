import datetime
import json
import os
import shutil
import setup_utils
import setup_non_priviliged
from print_colors import Color

print_color = Color()


def configure(data: dict, copy_data: dict, users: dict, dir: str):

    path = setup_utils.get_mount_path()

    setup_utils.mkdirs_as_user(dir=f'{path}/etc/firefox/policies')

    # Create missing user specific directories
    for user in ['admin', 'user']:
        for missing_dir in [f'/home/{user}/.config/environment.d/', f'/home/{user}/.local/share/applications/']:
            print(missing_dir)
            setup_utils.mkdirs_as_user(user=user, dir=missing_dir)

    setup_utils.disable_sudo_password("admin")

    try:
        setup_non_priviliged.install_yay()

    except Exception as e:
        print_color.print_error(
            "ERROR: Installation of yay failed! | %s" % (e))

    finally:
        setup_utils.reenable_sudo_password("admin")

    setup_utils.disable_sudo_password("admin")
    try:
        for pkg in data["aur_pkgs"]:
            setup_non_priviliged.install_aur_package(chroot=True, package=pkg)
    except:
        pass
    finally:
        setup_utils.reenable_sudo_password('admin')

    for _, v in copy_data.items():
        try:
            source = os.path.normpath(f"{dir}{v.get('source')}")
            destination = os.path.normpath(
                f"{path}{v.get('destination')}")
            if os.path.isdir(source):
                shutil.copytree(source, destination, dirs_exist_ok=True)
                print('Source dir: %s' % source)

            else:
                print("Source file %s" % source)
                shutil.copyfile(source, destination)
            if v.get('permissions'):
                shutil.chown(path=destination, user=v.get('permissions').get(
                    'uid'), group=v.get('permissions').get('gid'))

        except Exception as e:
            print("error %s" % e)
            pass

    for user, user_data in users.items():

        for app in os.listdir(os.path.join(dir, 'general', 'data', 'DesktopEntries')):
            setup_utils.add_desktop_app(file_path=os.path.join(
                dir, 'general', 'data', 'DesktopEntries', app), user=user, visible_apps=user_data['desktop'])

        for app in os.listdir('/mnt/archinstall/usr/share/applications/'):
            setup_utils.add_desktop_app(file_path=os.path.join(
                '/mnt/archinstall/usr/share/applications/', app), user=user, visible_apps=user_data['desktop'])

    for cmd in data["final_cmds"]:
        setup_utils.run_command(cmd)
    setup_utils.enable_group_for_sudo('wheel')

    with open("/var/log/os", "a") as f:
        f.write("Version 1.0: %s" % datetime.date.today().strftime('%Y-%m-%d'))


if __name__ == "__main__":
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split("scripts")[0]
