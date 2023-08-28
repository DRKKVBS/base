import shutil
import os
import json
import subprocess
import re


# Get the largest disk from the list
def get_largest_disk(disk_lst):
    """Get the largest disk from the list"""
    disks = {}
    diskSize = []
    for d in disk_lst.split("\n\n\n"):
        disk = d.split("\n")[0]
        size = int(re.findall("(?<=,\s)(.*)(?=\sbytes)", disk)[0])
        name = re.findall("(?<=Disk\s)(.*)(?=:)", disk)[0]
        diskSize.append(size)
        disks[name] = size

    for k, v in disks.items():
        if v == max(diskSize):
            large_disk = k
            return large_disk


# Read the hardware of the system
def get_hw():
    """Read the hardware of the system"""
    hardInfo = {}
    # Disks
    hardInfo["disk"] = get_largest_disk(subprocess.run(["fdisk", "-l"], check=True,
                                                       text=True, capture_output=True).stdout)
    # VGA
    for e in subprocess.run(["lspci"], check=True,
                            text=True, capture_output=True).stdout.splitlines():
        if "VGA" in e:
            hardInfo["vga"] = e
    return hardInfo


# Create the config json
def create_config(data):
    """Create the config file"""

    vga_driver = get_hw()['vga']

    # Check the VGA
    if vga_driver is None:
        vga = "All open-source (default)"
    elif "nvidia" in vga_driver.lower():
        vga = "Nvidia"
    elif "intel" in vga_driver.lower():
        vga = "Intel (open-source)"
    elif any(substring in vga_driver.lower() for substring in ["vmware", "virtualbox"]):
        vga = "VMware / VirtualBox (open-source)"
    elif "amd" in vga_driver.lower():
        vga = "AMD / ATI (open-source)"
    else:
        vga = "All open-source (default)"

    config = {
        "additional-repositories": [],
        "archinstall-language": "German",
        "audio_config": {
            "audio": "pipewire"
        },
        "bootloader": "Grub",
        "config_version": "2.6.0",
        "debug": False,
        "disk_config": {
            "config_type": "default_layout",
            "device_modifications": [
                {
                    "device": get_hw()["disk"],
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
                                    "value": 250148290560
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
                                "value": 20
                            },
                            "status": "create",
                            "type": "primary"
                        }
                    ],
                    "wipe": True
                }
            ],
        },
        "hostname": "drk",
        "kernels": ["linux"],
        "locale_config": {
            "kb_layout": "de",
            "sys_enc": "UTF-8",
            "sys_lang": "de_DE"
        },
        "mirror_config": {
            "mirror_regions": {
                "Germany": [
                    "https://mirror.informatik.tu-freiberg.de/arch/$repo/os/$arch"
                    "http://ftp.wrz.de/pub/archlinux/$repo/os/$arch"
                    "https://ftp.fau.de/archlinux/$repo/os/$arch"
                    "http://mirrors.xtom.de/archlinux/$repo/os/$arch"
                    "http://ftp.uni-kl.de/pub/linux/archlinux/$repo/os/$arch"
                    "https://mirror.sunred.org/archlinux/$repo/os/$arch"
                    "http://mirror.mikrogravitation.org/archlinux/$repo/os/$arch"
                    "http://ftp.halifax.rwth-aachen.de/archlinux/$repo/os/$arch"
                    "https://arch.phinau.de/$repo/os/$arch"
                    "http://os.codefionn.eu/archlinux/$repo/os/$arch"
                    "https://ftp.spline.inf.fu-berlin.de/mirrors/archlinux/$repo/os/$arch"
                    "http://ftp.hosteurope.de/mirror/ftp.archlinux.org/$repo/os/$arch"
                    "http://mirror.lcarilla.de/archlinux/$repo/os/$arch"
                    "http://ftp.tu-chemnitz.de/pub/linux/archlinux/$repo/os/$arch"
                    "https://mirror.pseudoform.org/$repo/os/$arch"
                    "https://archlinux.thaller.ws/$repo/os/$arch"
                    "https://ftp.wrz.de/pub/archlinux/$repo/os/$arch"
                    "https://mirror.fra10.de.leaseweb.net/archlinux/$repo/os/$arch"
                    "https://mirror.mikrogravitation.org/archlinux/$repo/os/$arch"
                    "http://mirror.cmt.de/archlinux/$repo/os/$arch"
                    "http://arch.phinau.de/$repo/os/$arch"
                    "http://arch.jensgutermuth.de/$repo/os/$arch"
                    "http://mirror.moson.org/arch/$repo/os/$arch"
                    "http://mirror.ubrco.de/archlinux/$repo/os/$arch"
                    "https://mirror.ubrco.de/archlinux/$repo/os/$arch"
                    "https://archlinux.richard-neumann.de/$repo/os/$arch"
                    "https://archlinux.homeinfo.de/$repo/os/$arch"
                    "https://mirror.iusearchbtw.nl/$repo/os/$arch"
                    "https://mirrors.xtom.de/archlinux/$repo/os/$arch"
                    "https://mirror.metalgamer.eu/archlinux/$repo/os/$arch"
                    "http://archlinux.mirror.iphh.net/$repo/os/$arch"
                    "https://pkg.fef.moe/archlinux/$repo/os/$arch"
                    "https://mirror.f4st.host/archlinux/$repo/os/$arch"
                    "http://mirrors.n-ix.net/archlinux/$repo/os/$arch"
                    "https://mirror.bethselamin.de/$repo/os/$arch"
                    "http://mirror.clientvps.com/archlinux/$repo/os/$arch"
                    "https://dist-mirror.fem.tu-ilmenau.de/archlinux/$repo/os/$arch"
                    "http://packages.oth-regensburg.de/archlinux/$repo/os/$arch"
                    "http://linux.rz.rub.de/archlinux/$repo/os/$arch"
                    "http://mirror.netcologne.de/archlinux/$repo/os/$arch"
                    "https://mirrors.janbruckner.de/archlinux/$repo/os/$arch"
                    "http://ftp.uni-bayreuth.de/linux/archlinux/$repo/os/$arch"
                    "http://archlinux.honkgong.info/$repo/os/$arch"
                    "http://ftp.gwdg.de/pub/linux/archlinux/$repo/os/$arch"
                    "https://mirror.cmt.de/archlinux/$repo/os/$arch"
                    "https://packages.oth-regensburg.de/archlinux/$repo/os/$arch"
                    "https://ftp.agdsn.de/pub/mirrors/archlinux/$repo/os/$arch"
                    "http://mirror.f4st.host/archlinux/$repo/os/$arch"
                    "https://arch.unixpeople.org/$repo/os/$arch"
                    "http://archlinux.thaller.ws/$repo/os/$arch"
                    "https://arch.jensgutermuth.de/$repo/os/$arch"
                    "https://mirrors.n-ix.net/archlinux/$repo/os/$arch"
                    "https://mirror.kumi.systems/archlinux/$repo/os/$arch"
                    "http://arch.mirror.zachlge.org/$repo/os/$arch"
                    "http://mirror.wtnet.de/archlinux/$repo/os/$arch"
                    "https://mirror.dogado.de/archlinux/$repo/os/$arch"
                    "http://ftp-stud.hs-esslingen.de/pub/Mirrors/archlinux/$repo/os/$arch"
                    "https://mirror.lcarilla.de/archlinux/$repo/os/$arch"
                    "http://mirrors.niyawe.de/archlinux/$repo/os/$arch"
                    "http://mirror.sunred.org/archlinux/$repo/os/$arch"
                    "https://mirror.clientvps.com/archlinux/$repo/os/$arch"
                    "https://mirror.wtnet.de/archlinux/$repo/os/$arch"
                    "https://os.codefionn.eu/archlinux/$repo/os/$arch"
                    "http://ftp.spline.inf.fu-berlin.de/mirrors/archlinux/$repo/os/$arch"
                    "http://mirror.fra10.de.leaseweb.net/archlinux/$repo/os/$arch"
                    "http://ftp.agdsn.de/pub/mirrors/archlinux/$repo/os/$arch"
                    "https://mirror.moson.org/arch/$repo/os/$arch"
                    "https://mirror.pagenotfound.de/archlinux/$repo/os/$arch"
                    "http://mirror.informatik.tu-freiberg.de/arch/$repo/os/$arch"
                    "https://de.arch.mirror.kescher.at/$repo/os/$arch"
                    "https://mirror.selfnet.de/archlinux/$repo/os/$arch"
                    "https://arch.mirror.zachlge.org/$repo/os/$arch"
                    "http://mirror.23m.com/archlinux/$repo/os/$arch"
                    "http://ftp.fau.de/archlinux/$repo/os/$arch"
                    "http://mirrors.janbruckner.de/archlinux/$repo/os/$arch"
                    "https://mirror.netcologne.de/archlinux/$repo/os/$arch"
                    "http://mirror.united-gameserver.de/archlinux/$repo/os/$arch"
                    "http://mirror.metalgamer.eu/archlinux/$repo/os/$arch"
                    "https://mirror.23m.com/archlinux/$repo/os/$arch"
                    "https://mirrors.niyawe.de/archlinux/$repo/os/$arch"
                    "http://ftp.uni-hannover.de/archlinux/$repo/os/$arch"
                    "http://artfiles.org/archlinux.org/$repo/os/$arch"
                    "http://mirror.selfnet.de/archlinux/$repo/os/$arch"
                    "http://mirror.kumi.systems/archlinux/$repo/os/$arch"
                    "https://ftp.halifax.rwth-aachen.de/archlinux/$repo/os/$arch"
                    "https://appuals.com/archlinux/$repo/os/$arch"
                    "http://mirror.pagenotfound.de/archlinux/$repo/os/$arc"

                ]
            }
        },
        "nic": {
            "dhcp": True,
            "dns": "null",
            "gateway": "null",
            "iface": "null",
            "ip": "null",
            "type": "nm"
        },
        "no_pkg_lookups": False,
        "ntp": True,
        "offline": False,
        "packages": data["pkgs"],
        "parallesl downloads": 0,
        "profile_config": {
            "gfx_driver": vga,
            "greeter": "gdm",
            "profile": {}
        },
        "scripts": "guided",
        "silent": True,
        "swap": True,
        "sys-encoding": "UTF-8",
        "sys-language": "de_DE",
        "timezone": "Europe/Berlin",
        "version": "2.6.0"
    }
    return config


# Create credentitals
def create_creds(users):
    """Create credentitals"""

    user_lst = []

    for k, v in users.items():

        user_lst.append(v['!creds'])

    creds = {
        "!users": user_lst
    }
    return creds


def install(file_directory: str):
  # Get pkgs and services to install
    with open(f'{file_directory}/install.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        f.close()

    with open(f'{file_directory}/users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
        f.close()

    config = create_config(data)
    creds = create_creds(users)

    try:
        print('THE INSTALLATION HAS BEEN STARTED')
        subprocess.run(["archinstall",
                        "--config", json.dumps(config),
                        "--creds", json.dumps(creds), "--silent"],
                       check=True, text=True)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    path = os.path.realpath(
        os.path.dirname(__file__)).split('scripts')[0] + 'data'

    install(path)
