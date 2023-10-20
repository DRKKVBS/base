import os
import shutil
from print_colors import Color


# os.normpath()

print_color = Color()

if not os.path.exists('/mnt/archinstall/home/admin/.local/share/applications') and len(os.listdir('/mnt/archinstall/home/admin/.local/share/applications')):
    print_color.print_error('AccountServices are not setup')

if len(os.listdir('/mnt/archinstall/home/admin/.local/share/applications')):
    print_color.print_error('AccountServices are not setup')
