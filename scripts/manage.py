import json
import subprocess
import os
import argparse
import shutil
import git
import installation
import setup_sudo
import setup_non_sudo
import utils


if __name__ == '__main__':

    # Directories
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]

    script_directory = os.path.join(root_directory, 'scripts')

    data_directory = os.path.join(root_directory, 'data')
    download_directory = os.path.join(root_directory, 'download')

    # Initialize parser
    parser = argparse.ArgumentParser(prog='DRK Ach Configurator',
                                     description='Configures the the Arch Linux, after the OS Installation.',
                                     epilog='Text at the bottom of help.')

    # Adding optional argument
    parser.add_argument('-t', '--Type', action='store', required=True, type=str, choices=['THIN', 'MOBILE'],
                        help='Type of Configuration.')

    parser.add_argument('-hn', '--Hostname', action='store', type=str,
                        help='The hostname of the new system.')

    parser.add_argument('-u', '--upate', action='store',
                        type=float, help='The Version you want to be installed.')

    # Read arguments from command line
    args = parser.parse_args()

    if args.Type == 'THIN':
        git.Repo.clone_from('https://github.com/DRKKVBS/thin_client',
                            download_directory)
        branch = 'thin_client'

    else:
        git.Repo.clone_from('https://github.com/DRKKVBS/mobile_client',
                            download_directory)
        branch = 'mobile_client'

    # Merge config files
    for config_file in ['install.json', 'setup.json', 'users.json']:
        if not os.path.exists(f'{download_directory}/data/{config_file}'):
            continue
        with open(f'{data_directory}/{config_file}', 'r+') as f_setup, open(f'{download_directory}/data/{config_file}', 'r') as f_download:
            setup_data = json.load(f_setup)
            setup_download = json.load(f_download)
            merged_data = utils.merge_and_update_dicts(
                setup_data, setup_download)
            f_setup.seek(0)
            f_setup.truncate()
            json.dump(merged_data, f_setup)

    utils.copy_recursive(copy_src=download_directory+'/data', copy_dst=data_directory,
                         ignore=['setup.json', 'install.json', 'users.json'], dir_mode=644, ownership=('root', 'root'))

    #installation.install(data_directory, args.Hostname)

    utils.copy_recursive(
        root_directory, '/mnt/archinstall/tmp/', 777, ('root', 'root'), ignore=[])

    subprocess.run(
        'arch-chroot /mnt/archinstall python /tmp/scripts/configuration.py')

    # Delete Downloaded git repo
    shutil.rmtree(os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0])
