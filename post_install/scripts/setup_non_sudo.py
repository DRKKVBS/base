import json
import os
import shutil
import subprocess


def setup(root_directory: str):
    with open(f'{root_directory}/config.json', 'r') as f:
        setup_json = json.load(f)
        aur_pkgs = setup_json['post_install']['aur_pkgs']

    # Install yay
    print('Installing yay')
    subprocess.Popen(args='git clone https://aur.archlinux.org/yay && cd yay/ && makepkg -si --noconfirm && cd && rm -rf yay/', group="admin", user="admin", shell=False)

    # Install third party packages
    for pkg in aur_pkgs:
        try:
            print(f'Installing {pkg}')
            subprocess.run(['yay', '-S', pkg, '--noconfirm'], shell=False)
        except Exception as e:
            print(
                f'AN ERROR OCCURED! {str(pkg).upper()} COULD NOT BE INSTALLED!')
            print(e)
        else:
            print(f'Installation of {pkg} was succesfull')


if __name__ == "__main__":
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    setup(root_directory)
