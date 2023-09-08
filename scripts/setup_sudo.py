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
                    f'chattr -i /home/{u}/.local/share/applications/{file}', shell=True)
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
                f'chattr +i /home/{u}/.local/share/applications/{file}', shell=True)
        subprocess.run(
            f'chattr +i /home/{u}/.local/share/applications/', shell=True)

    # # Copy directories
    for k, v in {f'{data_directory}/AccountsService': '/var/lib/AccountsService', f'{data_directory}/dconf': '/etc/dconf',
                 f'{data_directory}/drk-logo.png': '/usr/share/logos', f'{data_directory}/firefox/policies': '/etc/firefox/policies/'}.items():
        if not os.path.exists(v):
            os.makedirs(v)
        if os.path.isdir(k):
            shutil.copytree(k,v, dirs_exist_ok=True)
        else:
            shutil.copyfile(k,v)


        

    # Copy files
    for k, v in {f'{data_directory}/firefox/FirefoxAutostart.desktop': '/etc/xdg/autostart/FirefoxAutostart.desktop',
                 f'{data_directory}/gdm.conf': '/etc/gdm/custom.conf', f'{data_directory}/grub': '/etc/default/grub'}.items():
        shutil.copyfile(k, v)

    # Update dconf db, remove user from "wheel" group, change user password, create correct timezone, update grub config
    for cmd in ['dconf update', 'usermod -G user user', 'passwd -d user', 'grub-mkconfig -o /boot/grub/grub.cfg']:
        print(cmd)
        subprocess.run(cmd, shell=True)

    if os.path.exists(f'{script_directory}/setup_sudo_add.py'):
        subprocess.run(f'python {script_directory}/setup_sudo_add.py')


if __name__ == '__main__':
    dwn_dir = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0] + 'data'
    script_dir = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0] + 'scripts'
    setup(dwn_dir, script_dir)
