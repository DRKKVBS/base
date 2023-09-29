import json
import pwd
import subprocess
import os
import shutil


def setup(data_directory: str, script_directory: str):

    with open(f'{data_directory}/config.json', 'r') as f:
        setup_json = json.load(f)
        post_install_json = setup_json['post_install']
        users_json = setup_json['users']

    # Setup user specific configuration
    for u, d in users_json.items():

        uid = pwd.getpwnam(u).pw_uid
        gid = pwd.getpwnam(u).pw_gid

        os.makedirs(f'/home/{u}/.config/environment.d/')
        os.chown(f'/home/{u}/.config/', uid=uid, gid=gid)
        os.chown(f'/home/{u}/.config/environment.d', uid=uid, gid=gid)
        with open(f'/home/{u}/.config/environment.d/variables.conf', 'x') as f:
            f.write(
                f"DCONF_PROFILE={d['environment_variables']['DCONF_PROFILE']}")

        # Desktop Entries
        desktop_entries = d["desktop"]

        # Create Directories if they do not exist
        if not os.path.exists(f'/home/{u}/.local/share/applications/'):
            os.makedirs(f'/home/{u}/.local/share/applications/')
            os.chown(f'/home/{u}/.local/', uid=uid, gid=gid)
            os.chown(f'/home/{u}/.local/share/', uid=uid, gid=gid)
            os.chown(f'/home/{u}/.local/share/applications/', uid=uid, gid=gid)

        # Copy the Desktop Files into the new directory
        for file in os.listdir(f'{data_directory}/DesktopEntries/'):
            shutil.copyfile(os.path.join(
                f'{data_directory}/DesktopEntries/', file), f'/home/{u}/.local/share/applications/{file}')

        # Make Dekstop Entries hidden
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
            # Make File immutable
            subprocess.run(
                ['chattr', '+i', f'/home/{u}/.local/share/applications/{file}'], shell=False)
        # Make the directory immutable
        subprocess.run(
            ['chattr', '+i', f'/home/{u}/.local/share/applications/'], shell=False)

        # Setup AccountsServive
        with open(f'/var/lib/AccountsService/users/{u}', 'wx') as f:
            for entry, value in d['accountsservice']:
                f.write(f'{entry}={value}')
        shutil.copy(f'{data_directory}/images/{u}.jpg',
                    f'/var/lib/AccountsService/icons/')

    # Setup dconf
    for profile, db in post_install_json['dconf']['profiles']:
        with open(f'/etc/dconf/profiles/{profile}'):
            for user_db in db['user-dbs']:
                f.write('user-db=', user_db)
            for system_db in db['system-dbs']:
                f.write('system-db=', system_db)
            for file_db in db['file-dbs']:
                f.write('file-db=', file_db)

    for k, v in post_install_json['dconf']['dbs'].item():
        if not os.path.exists(f'/etc/dconf/db/{k}'):
            os.mkdir(f'/etc/dconf/db/{k}')
        if 'locks' in v.keys():
            os.mkdir(f'/etc/dconf/db/{k}/locks')
            for file, content in v['locks']:
                with open(f'/etc/dconf/db/{k}/locks/{file}') as f:
                    f.writelines(content)


    # Copy directories
    for k, v in {f'{data_directory}/dconf': '/etc/dconf',
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
