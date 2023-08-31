import os
import shutil
import subprocess
import setup_sudo


def configure(file_directory):

    data_directory = os.path.join(file_directory, 'data')

    setup_sudo.setup(data_directory)

    subprocess.run(
        'sudo -i -u admin; python /home/admin/drk-arch/scripts/setup_non_sudo.py', shell=True)


if __name__ == '__main__':
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    configure(root_directory)
