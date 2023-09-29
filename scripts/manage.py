import json
import shutil
import subprocess
import os
import argparse
import installation
import utils


if __name__ == '__main__':

    # Directories
    root_directory = '/base'
    script_directory = os.path.join(root_directory, 'scripts')

    data_directory = os.path.join(root_directory, 'data')
    download_directory = os.path.join(root_directory, 'download')

    # Initialize parser
    parser = argparse.ArgumentParser(prog='DRK Ach Configurator',
                                     description='Configures the the Arch Linux, after the OS Installation.',
                                     epilog='Text at the bottom of help.')

    # Adding optional argument
    parser.add_argument('-t', '--Type', action='store', required=True, type=str, choices=['thin', 'mobile', 'mpg', 'hnr'],
                        help='Type of Device.')

    parser.add_argument('-c', '--Configuration', action='store', required=True, type=str,
                        choices=['base', 'mpg', 'hnr'], help='Type of Configuration to be used.')

    parser.add_argument('-hn', '--Hostname', action='store', type=str,
                        help='The hostname of the new system.')

    parser.add_argument('-u', '--upate', action='store',
                        type=float, help='The Version you want to be installed.')

    # Read arguments from command line
    args = parser.parse_args()

    match args.Type:
        case 'thin':
            branch = 'thin-client'
        case 'mobile':
            branch = 'mobile-client'
        case _:
            branch = 'thin-client'

    match args.Configuration:
        case 'hnr':
            config = 'hnr'
        case 'mpg':
            config = 'mpg'
        case _:
            config = 'base'

    if args.Hostname != None:
        hostname = args.Hostname
    else:
        hostname = f'drk-bs-{args.Type}-{args.Configuration}'

    # Merge and copy configuration files
    with open(f'{root_directory}/configs/base.json', 'r') as f_base, open(f'{root_directory}/configs/{args.Configuration}.json', 'r') as f_config, open(f'{root_directory}/type/{args.Type}/platform_config.json', 'r') as f_platform_config, open(f'{root_directory}/configs/config.json', 'x') as f_merged:
        base_data = json.load(f_base)
        config_data = json.load(f_config)
        platform_config_data = json.load(f_platform_config)
        merged_data = utils.merge_and_update_dicts(
            base_data, config_data)
        merged_data = utils.merge_and_update_dicts(
            merged_data, platform_config_data)
        json.dump(merged_data, f_merged)
    if not os.path.exists(f'{root_directory}/post_install/'):
        os.mkdir(f'{root_directory}/post_install/')
    shutil.copy(f'{root_directory}/configs/config.json',
                f'{root_directory}/post_install/')

    # Start the linux installation
    #installation.install(f'{root_directory}/configs/', hostname)

    # Copy the files for post install configuration
    shutil.copytree(
        data_directory, f'{root_directory}/post_install/', dirs_exist_ok=True)
    shutil.copytree(f'{root_directory}/type/{args.Type}',
                    f'{root_directory}/post_install/', dirs_exist_ok=True)
    shutil.copytree(f'{root_directory}/post_install/',
                    '/mnt/archinstall/home/admin/drk-arch/', dirs_exist_ok=True)

    # Start the configuration in the arch-chroot environment
    # subprocess.run(
    #     ['arch-chroot', '/mnt/archinstall', 'python', '/home/admin/drk-arch/scripts/configuration.py'], shell=False)

    # Delete Downloaded git repo
    shutil.rmtree(os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0])
