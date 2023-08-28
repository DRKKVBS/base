import os
import setup_sudo
import setup_non_sudo

root_directory = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0]

script_directory = os.path.join(root_directory, 'scripts')
data_directory = os.path.join(root_directory, 'data')

setup_sudo.setup(data_directory)

setup_non_sudo.setup(data_directory)

