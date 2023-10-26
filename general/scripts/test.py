import os
import shutil
from print_colors import Color
import setup_utils


# os.normpath()

print_color = Color()
path = '/mypath/'

user = '/test/'

print(os.path.join(path, '/home/', user, '/.local/share/applications/', 'app'))
print(os.path.join('/','home', 'local','share/applications/', 'app'))


