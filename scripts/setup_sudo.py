import json
import pwd
import subprocess
import os
import shutil
import setup_priviliged_type
import utils


def setup(root_directory: str):

    with open(f'{root_directory}/config.json', 'r') as f:
        setup_json = json.load(f)
        post_install_json = setup_json['post_install']
        users_json = setup_json['users']

    # Setup user specific configuration
    for u, d in users_json.items():

        uid = pwd.getpwnam(u).pw_uid
        gid = pwd.getpwnam(u).pw_gid

        os.makedirs(f'/home/{u}/.config/environment.d/', exist_ok=True)
        os.chown(f'/home/{u}/.config/', uid=uid, gid=gid)
        os.chown(f'/home/{u}/.config/environment.d', uid=uid, gid=gid)
        with open(f'/home/{u}/.config/environment.d/variables.conf', 'w+') as f:
            f.write(
                f"DCONF_PROFILE={d['environment_variables']['DCONF_PROFILE']}\n")

        # Desktop Entries
        desktop_entries = d["desktop"]

        # Create Directories if they do not exist
        if not os.path.exists(f'/home/{u}/.local/share/applications/'):
            os.makedirs(f'/home/{u}/.local/share/applications/', exist_ok=True)
            os.chown(f'/home/{u}/.local/', uid=uid, gid=gid)
            os.chown(f'/home/{u}/.local/share/', uid=uid, gid=gid)
            os.chown(f'/home/{u}/.local/share/applications/', uid=uid, gid=gid)

        # Copy the Desktop Files into the new directory
        for file in os.listdir(f'{root_directory}/data/DesktopEntries/'):
            shutil.copyfile(os.path.join(
                f'{root_directory}/data/DesktopEntries/', file), f'/home/{u}/.local/share/applications/{file}')

        setup_priviliged_type.add_desktop_apps(root_directory, u)

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
        with open(f'/var/lib/AccountsService/users/{u}', 'w+') as f:
            for entry, value in d['accountsservice'].items():
                f.write(f'{entry}={value}\n')

    # Setup dconf
    utils.create_dir_not_exists('/etc/dconf/profiles/')
    utils.create_dir_not_exists('/etc/dconf/db/')
    for profile, db in post_install_json['dconf']['profiles'].items():
        with open(f'/etc/dconf/profiles/{profile}', 'w+') as f:
            for user_db in db['user-dbs']:
                f.write('user-db=' + user_db+'\n')
            for system_db in db['system-dbs']:
                f.write('system-db=' + system_db+'\n')
            for file_db in db['file-dbs']:
                f.write('file-db=' + file_db+'\n')

    for k, v in post_install_json['dconf']['dbs'].items():
        utils.create_dir_not_exists(f'/etc/dconf/db/{k}')
        if 'locks' in v.keys():
            utils.create_dir_not_exists(f'/etc/dconf/db/{k}.d/locks/')
            for file, content in v['locks'].items():
                with open(f'/etc/dconf/db/{k}.d/locks/{file}', 'w+') as f:
                    f.write(content+'\n')
        for k1, v1 in v.items():
            with open(f'/etc/dconf/db/{k}.d/{k1}', 'w+') as f:
                for k2, v2 in v1.items():
                    f.write(f'{k2}={v2}\n')

    # Copy Logos
    utils.create_dir_not_exists('/usr/share/logos/')
    shutil.copytree(f'{root_directory}/data/images/logos/',
                    '/usr/share/logos/', dirs_exist_ok=True)

    # Copy Icons
    utils.create_dir_not_exists('/var/lib/AccountsService/icons')
    shutil.copytree(f'{root_directory}/data/images/icons/',
                    '/var/lib/AccountsService/icons', dirs_exist_ok=True)

    # Firefox
    utils.create_dir_not_exists('/usr/share/firefox/')
    shutil.copytree(f'{root_directory}/data/firefox/', '/usr/share/firefox/')
    setup_priviliged_type.setup(root_directory)
    setup_priviliged_type.add_autostart_apps(root_directory)

    with open('/etc/gdm/custom.conf', 'w+') as f, open(f'{root_directory}/gdm.conf', 'r') as f1:
        f.write(f1.read())

    with open('/etc/default/grub', 'w+') as f, open(f'{root_directory}/grub', 'r') as f1:
        f.write(f1.read())

    setup_priviliged_type.setup_rest(root_directory)

    # Update dconf db, remove user from "wheel" group, change user password, create correct timezone, update grub config
    for cmd in [['dconf', 'update'], ['usermod', '-G', 'user', 'user'],
                ['passwd', '-d', 'user'], ['grub-mkconfig', '-o', '/boot/grub/grub.cfg']]:
        subprocess.run(cmd, shell=False)

    # if os.path.exists(f'{script_directory}/setup_sudo_add.py'):
    #     subprocess.run(
    #         ['python', f'{script_directory}/setup_sudo_add.py'], shell=False)


def disable_sudo_password():
    with open('/etc/sudoers.d/00_admin', 'w+') as f:
        f.write('admin ALL=(ALL) NOPASSWD: ALL')


def reenable_sudo_password():
    os.remove('/etc/sudoers.d/00_admin')


if __name__ == '__main__':
    root_dir = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    setup(root_dir)
