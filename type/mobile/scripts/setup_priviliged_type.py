import os
import shutil


def setup_firefox(root_directory: str):
    # Create Firefox Policies
    if not os.path.exists('/etc/firefox/policies/'):
        os.makedirs('/etc/firefox/policies/', exist_ok=True)
    shutil.copyfile(f'{root_directory}/data/firefox/policies.json',
                    '/etc/firefox/policies/policies.json')
    shutil.copyfile(f'{root_directory}/data/firefox/DRK_Rechenzentrum.html',
                    '/usr/share/firefox/DRK_Rechenzentrum.html')
    shutil.copytree(f'{root_directory}/data/firefox/DRK_Rechenzentrum_files/',
                    '/usr/share/firefox/', dirs_exist_ok=True)


def add_autostart_apps(root_directory: str):
    # Setup Autostart apps
    shutil.copyfile(f'{root_directory}/data/autostart/myWorkspaceAutostart.desktop',
                    '/etc/xdg/autostart/myWorkspaceAutostart.desktop')


def add_desktop_apps(root_directory: str, user: str):
    # Setup Desktop apps
    shutil.copyfile(f'{root_directory}/data/DesktopEntries/myWorkspace.desktop',
                    f'/home/{user}/.local/share/applications/myWorkspace.desktop')
    
def setup_rest(root_directory: str):
    shutil.copyfile(f'{root_directory}/data/wifi/wifi_backend.conf',
                    '/etc/NetworkManager/conf.d/wifi_backend.conf')
