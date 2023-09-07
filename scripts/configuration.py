import os
import subprocess
import setup_sudo


def configure(file_directory, script_directory):

    data_directory = os.path.join(file_directory, 'data')

    setup_sudo.setup(data_directory, script_directory)

    subprocess.run(
        'sudo -i -u admin', input='python /home/admin/drk-arch/scripts/setup_non_sudo.py', text=True, shell=True)


if __name__ == '__main__':
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    scripts_directory = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0] + 'scripts'
    configure(root_directory, scripts_directory)
