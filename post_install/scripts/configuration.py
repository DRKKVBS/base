import json
import os
import shutil
import subprocess
import setup_sudo


def configure(root_directory: str):

    with open(f'{root_directory}/config.json', 'r') as f:
        setup_json = json.load(f)
        post_install_json = setup_json['post_install']

    setup_sudo.disable_sudo_password()
    subprocess.run(
        ['sudo', '-i', '-u', 'admin'], input=f'bash /home/admin/drk-arch/scripts/setup_non_sudo.sh {" ".join(post_install_json["aur_pkgs"])}', text=True, shell=False)
    setup_sudo.reenable_sudo_password()

    # setup_sudo.setup(data_directory, script_directory)

    # os.chmod('/home/admin/after_reboot.sh', mode=744)
    # subprocess.run(['/home/admin/after_reboot.sh'], shell=False)

    with open('/var/log/os', 'w+') as f:
        f.write('Version 1.0')


if __name__ == '__main__':
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    configure(root_directory)
