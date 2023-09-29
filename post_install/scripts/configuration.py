import os
import shutil
import subprocess
import setup_sudo


def configure(file_directory, script_directory):

    data_directory = os.path.join(file_directory, 'data')

    setup_sudo.setup(data_directory, script_directory)

    subprocess.run(
        ['sudo', '-i', '-u', 'admin'], input='python /home/admin/drk-arch/scripts/setup_non_sudo.py', text=True, shell=False)
    
    os.chmod('/home/admin/after_reboot.sh', mode=744)
    subprocess.run(['/home/admin/after_reboot.sh'], shell=False)

    with open('/var/log/os', 'w') as f:
        f.write('Version 1.0')


if __name__ == '__main__':
    root_directory = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]
    scripts_directory = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0] + 'scripts'
    configure(root_directory, scripts_directory)
