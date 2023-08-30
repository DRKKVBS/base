import os
import shutil
import setup_sudo
import setup_non_sudo


def configure(file_directory):

        

        data_directory = os.path.join(file_directory, 'data')

        setup_sudo.setup(data_directory)

        setup_non_sudo.setup(data_directory)

        


if __name__ == '__main__': 
    root_directory = os.path.realpath(
                os.path.dirname(__file__)).split('scripts')[0]
    configure(root_directory)

