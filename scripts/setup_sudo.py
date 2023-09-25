import json
import pwd
import subprocess
import os
import shutil
import utils


def setup(data_directory: str, script_directory: str):

    with open(f'{data_directory}/users.json', 'r') as f:
        users_json = json.load(f)

    # Setup user specific configuration
    for u, d in users_json.items():

        uid = pwd.getpwnam(u).pw_uid
        gid = pwd.getpwnam(u).pw_gid

        if not os.path.exists(f'/home/{u}/.config/environment.d/'):
            os.makedirs(f'/home/{u}/.config/environment.d/')
            os.chown(f'/home/{u}/.config/', uid=uid, gid=gid)
            os.chown(f'/home/{u}/.config/environment.d', uid=uid, gid=gid)
        shutil.copyfile(f'{data_directory}/EnvironmentVariables/{u}',
                        f'/home/{u}/.config/environment.d/variable.conf')

        # Desktop Entries
        desktop_entries = d["desktop"]

        if not os.path.exists(f'/home/{u}/.local/share/applications/'):
            os.makedirs(f'/home/{u}/.local/share/applications/')
            os.chown(f'/home/{u}/.local/', uid=uid, gid=gid)
            os.chown(f'/home/{u}/.local/share/', uid=uid, gid=gid)
            os.chown(f'/home/{u}/.local/share/applications/', uid=uid, gid=gid)

        for file in os.listdir(f'{data_directory}/DesktopEntries/'):
            shutil.copyfile(os.path.join(
                f'{data_directory}/DesktopEntries/', file), f'/home/{u}/.local/share/applications/{file}')

        for file in os.listdir('/usr/share/applications/'):
            content = ""
            if os.path.exists(f'/home/{u}/.local/share/applications/{file}'):
                subprocess.run(
                    ['chattr', '-i', f'/home/{u}/.local/share/applications/{file}'], shell=False)
            with open(f'/usr/share/applications/{file}', 'r') as f1:
                content = f1.read()
                if 'NoDisplay=true' in content:
                    continue
            shutil.copyfile(
                f'/usr/share/applications/{file}', f'/home/{u}/.local/share/applications/{file}')
            with open(f'/home/{u}/.local/share/applications/{file}', 'w') as f2:
                if 'NoDisplay=false' in content and file not in desktop_entries:
                    content = content.replace(
                        'NoDisplay=false', 'NoDisplay=true')
                elif file not in desktop_entries:
                    content = content.replace(
                        '[Desktop Entry]', '[Desktop Entry]\nNoDisplay=true')
                f2.write(content)
            subprocess.run(
                ['chattr', '+i', f'/home/{u}/.local/share/applications/{file}'], shell=False)
        subprocess.run(
            ['chattr', '+i', f'/home/{u}/.local/share/applications/'], shell=False)

    # # Copy directories
    for k, v in {f'{data_directory}/AccountsService': '/var/lib/AccountsService', f'{data_directory}/dconf': '/etc/dconf',
                 f'{data_directory}/logos': '/usr/share/logos', f'{data_directory}/firefox': '/etc/firefox/policies'}.items():
        if not os.path.exists(v):
            os.makedirs(v)
        shutil.copytree(k, v, dirs_exist_ok=True)

    # Copy files
    for k, v in {f'{data_directory}/firefox/myWorkspaceAutostart.desktop': '/etc/xdg/autostart/myWorkspaceAutostart.desktop',
                 f'{data_directory}/gdm.conf': '/etc/gdm/custom.conf', f'{data_directory}/grub': '/etc/default/grub'}.items():
        shutil.copyfile(k, v)

    # Update dconf db, remove user from "wheel" group, change user password, create correct timezone, update grub config
    for cmd in [['dconf', 'update'], ['usermod', '-G', 'user', 'user'],
                ['passwd', '-d', 'user'], ['grub-mkconfig', '-o', '/boot/grub/grub.cfg']]:
        subprocess.run(cmd, shell=False)

    if os.path.exists(f'{script_directory}/setup_sudo_add.py'):
        subprocess.run(
            ['python', f'{script_directory}/setup_sudo_add.py'], shell=False)


if __name__ == '__main__':
    root_dir = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    setup(os.path.join(root_dir, 'data'), os.path.join(root_dir, 'scripts'))
