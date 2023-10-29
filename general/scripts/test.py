import os
import shutil
from print_colors import Color
import setup_utils
import logging

print_color = Color()
path = '/mypath/'

user = '/test/'

print(os.path.join(path, '/home/', user, '/.local/share/applications/', 'app'))
print(os.path.join('/','home', 'local','share/applications/', 'app'))

print(os.path.join('/moun/','a/a', 'a/'))


logging.basicConfig(filename='./logs/example.log', encoding='utf-8', level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')


