import os
import json
import subprocess
import re


def install(data: dict, users: dict, hostname="drk-bs-client"):

    # Read out the hardware information of the system
    hardware_info = {}

    disks = {}
    diskSize = []
    for d in subprocess.run(['fdisk', '-l'], check=True,
                            text=True, capture_output=True).stdout.split("\n\n\n"):
        disk = d.split("\n")[0]
        size = int(re.findall("(?<=,\s)(.*)(?=\sbytes)", disk)[0])
        name = re.findall("(?<=Disk\s)(.*)(?=:)", disk)[0]
        diskSize.append(size)
        disks[name] = size

    for k, v in disks.items():
        if v == max(diskSize):
            hardware_info['disk'] = (k, v)

    for e in subprocess.run(['lspci'], check=True,
                            text=True, capture_output=True).stdout.splitlines():
        if "VGA" in e:
            hardware_info['vga'] = e

    # Set the correct VGA
    if hardware_info['vga'] is None:
        vga = "All open-source (default)"
    elif "nvidia" in hardware_info['vga'].lower():
        vga = "Nvidia"
    elif "intel" in hardware_info['vga'].lower():
        vga = "Intel (open-source)"
    elif any(substring in hardware_info['vga'].lower() for substring in ["vmware", "virtualbox"]):
        vga = "VMware / VirtualBox (open-source)"
    elif "amd" in hardware_info['vga'].lower():
        vga = "AMD / ATI (open-source)"
    else:
        vga = "All open-source (default)"

    config = {
        "additional-repositories": [],
        "archinstall-language": "German",
        "audio_config": None,
        "bootloader": "Grub",
        "config_version": "2.6.0",
        "debug": False,
        "disk_config": {
            "config_type": "default_layout",
            "device_modifications": [
                {
                    "device": hardware_info['disk'][0],
                    "partitions": [
                        {
                            "btrfs": [],
                            "flags": [
                                "Boot"
                            ],
                            "fs_type": "fat32",
                            "length": {
                                "sector_size": None,
                                "total_size": None,
                                "unit": "MiB",
                                "value": 512
                            },
                            "mount_options": [],
                            "mountpoint": "/boot",
                            "obj_id": "2c3fa2d5-2c79-4fab-86ec-22d0ea1543c0",
                            "start": {
                                "sector_size": None,
                                "total_size": None,
                                "unit": "MiB",
                                "value": 1
                            },
                            "status": "create",
                            "type": "primary"
                        },
                        {
                            "btrfs": [],
                            "flags": [],
                            "fs_type": "ext4",
                            "length": {
                                "sector_size": None,
                                "total_size": None,
                                "unit": "GiB",
                                "value": 20
                            },
                            "mount_options": [],
                            "mountpoint": "/",
                            "obj_id": "3e7018a0-363b-4d05-ab83-8e82d13db208",
                            "start": {
                                "sector_size": None,
                                "total_size": None,
                                "unit": "MiB",
                                "value": 513
                            },
                            "status": "create",
                            "type": "primary"
                        },
                        {
                            "btrfs": [],
                            "flags": [],
                            "fs_type": "ext4",
                            "length": {
                                "sector_size": None,
                                "total_size": {
                                    "sector_size": None,
                                    "total_size": None,
                                    "unit": "B",
                                    "value": hardware_info['disk'][1]
                                },
                                "unit": "Percent",
                                "value": 100
                            },
                            "mount_options": [],
                            "mountpoint": "/home",
                            "obj_id": "ce58b139-f041-4a06-94da-1f8bad775d3f",
                            "start": {
                                "sector_size": None,
                                "total_size": None,
                                "unit": "GiB",
                                "value": 2
                            },
                            "status": "create",
                            "type": "primary"
                        }
                    ],
                    "wipe": True
                }
            ]
        },
        "hostname": hostname,
        "kernels": ["linux"],
        "locale_config": {
            "kb_layout": "de",
            "sys_enc": "UTF-8",
            "sys_lang": "de_DE"
        },
        "mirror_config": {
            "mirror_regions": {
                "Germany": [
                    "http://ftp.wrz.de/pub/archlinux/$repo/os/$arch",
                    "https://ftp.fau.de/archlinux/$repo/os/$arch",
                    "http://mirrors.xtom.de/archlinux/$repo/os/$arch",
                    "http://ftp.uni-kl.de/pub/linux/archlinux/$repo/os/$arch",
                    "https://mirror.sunred.org/archlinux/$repo/os/$arch",
                    "http://mirror.mikrogravitation.org/archlinux/$repo/os/$arch",
                    "http://ftp.halifax.rwth-aachen.de/archlinux/$repo/os/$arch",
                    "https://arch.phinau.de/$repo/os/$arch",
                    "http://os.codefionn.eu/archlinux/$repo/os/$arch",
                    "http://mirror.lcarilla.de/archlinux/$repo/os/$arch",
                    "http://ftp.tu-chemnitz.de/pub/linux/archlinux/$repo/os/$arch",
                    "https://mirror.pseudoform.org/$repo/os/$arch",
                    "https://archlinux.thaller.ws/$repo/os/$arch",
                    "https://ftp.wrz.de/pub/archlinux/$repo/os/$arch",
                    "https://mirror.fra10.de.leaseweb.net/archlinux/$repo/os/$arch",
                    "https://mirror.mikrogravitation.org/archlinux/$repo/os/$arch",
                    "http://mirror.cmt.de/archlinux/$repo/os/$arch",
                    "http://arch.phinau.de/$repo/os/$arch",
                    "http://arch.jensgutermuth.de/$repo/os/$arch",
                    "http://mirror.moson.org/arch/$repo/os/$arch",
                    "http://mirror.ubrco.de/archlinux/$repo/os/$arch",
                    "https://mirror.ubrco.de/archlinux/$repo/os/$arch",
                    "https://archlinux.richard-neumann.de/$repo/os/$arch",
                    "https://archlinux.homeinfo.de/$repo/os/$arch",
                    "https://mirror.iusearchbtw.nl/$repo/os/$arch",
                    "https://mirror.metalgamer.eu/archlinux/$repo/os/$arch"
                ]
            }
        },
        "nic": {
            "dhcp": True,
            "dns": None,
            "gateway": None,
            "iface": None,
            "ip": None,
            "type": "nm"
        },
        "no_pkg_lookups": False,
        "ntp": True,
        "offline": False,
        "packages": data['pkgs'],
        "parallel downloads": 0,
        "gfx_driver": vga,
        "profile": None,
        "scripts": "guided",
        "services": data['services'],
        "silent": True,
        "swap": True,
        "sys-encoding": "UTF-8",
        "sys-language": "de_DE",
        "timezone": "Europe/Berlin",
        "version": "2.6.0"
    }

    # Creat the credential configuration
    user_lst = []

    for _, v in users.items():

        user_lst.append(v['!creds'])

    creds = {
        "!users": user_lst
    }

    try:
        print('THE INSTALLATION HAS BEEN STARTED')
        subprocess.run(['archinstall',
                        '--config', json.dumps(config),
                        '--creds', json.dumps(creds), '--silent'],
                       check=True, text=True)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    path = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0] + 'data'