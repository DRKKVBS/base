import json
import subprocess
import os
import argparse
import installation
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
    parser.add_argument('-t', '--Type', action='store', required=True, type=str, choices=['thin', 'mobile'],
                        help='Type of Configuration.')

    parser.add_argument('-hn', '--Hostname', action='store', type=str,
                        help='The hostname of the new system.')

    parser.add_argument('-u', '--upate', action='store',
                        type=float, help='The Version you want to be installed.')

    # Read arguments from command line
    args = parser.parse_args()

    if args.Type == 'thin':
        branch = 'thin-client'

    else:
        branch = 'mobile-client'

    subprocess.run(
        f'git clone https://github.com/DRKKVBS/{branch} {download_directory}', shell=True)
    hostname = f'drk-bs-{branch}'

    # Merge and copy configuration files
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

    utils.copy_recursive(copy_src=f'{download_directory}/data', copy_dst=data_directory,
                         ignore=['setup.json', 'install.json', 'users.json'], dir_mode=644, ownership=('root', 'root'))

    # Start the linux installation
    installation.install(data_directory, hostname)

    # # Copy the files
    # utils.copy_recursive(
    #     root_directory, '/mnt/archinstall/home/admin/drk-arch/', 777, ('root', 'root'), ignore=['installation.py', 'install.py'])

    # # Start the configuration in the arch-chroot environment
    # subprocess.run(
    #     'arch-chroot /mnt/archinstall python /home/admin/drk-arch/scripts/configuration.py', shell=True)

    # Delete Downloaded git repo
    # shutil.rmtree(os.path.realpath(
    #     os.path.dirname(__file__)).split('scripts')[0])
