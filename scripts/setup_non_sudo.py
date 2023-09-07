import json
import os
import shutil
import subprocess


def setup(file_directory: str):
    with open(f'{file_directory}/setup.json', 'r') as f:
        setup_json = json.load(f)
        aur_pkgs = setup_json['aur_pkgs']

    # Install yay
    print('Installing yay')
    # subprocess.Popen(args=["git", "clone", "https://aur.archlinux.org/yay", & & cd yay/; makepkg - si - -noconfirm; cd & & rm - rf yay/"], group="admin", user="admin")
    subprocess.run(
        'git clone https://aur.archlinux.org/yay && cd yay/; makepkg -si --noconfirm; cd && rm -rf yay/', shell=True)

    # Install third party packages
    for pkg in aur_pkgs:
        try:
            print(f'Installing {pkg}')
            subprocess.run(f'yay -S {pkg} --noconfirm', shell=True)
        except Exception as e:
            print(
                f'AN ERROR OCCURED! {str(pkg).upper()} COULD NOT BE INSTALLED!')
            print(e)
        else:
            print(f'Installation of {pkg} was succesfull')


if __name__ == "__main__":
    dwn_dir = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0] + 'data'
    setup(dwn_dir)
