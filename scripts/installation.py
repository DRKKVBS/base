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
        "mirror-region": {
            "Germany": {
                "http://mirror.23m.com/archlinux/$repo/os/$arch": True,
                "https://mirror.23m.com/archlinux/$repo/os/$arch": True,
                "http://ftp.agdsn.de/pub/mirrors/archlinux/$repo/os/$arch": True,
                "https://ftp.agdsn.de/pub/mirrors/archlinux/$repo/os/$arch": True,
                "https://appuals.com/archlinux/$repo/os/$arch": True,
                "http://artfiles.org/archlinux.org/$repo/os/$arch": True,
                "https://mirror.bethselamin.de/$repo/os/$arch": True,
                "http://mirror.clientvps.com/archlinux/$repo/os/$arch": True,
                "https://mirror.clientvps.com/archlinux/$repo/os/$arch": True,
                "http://mirror.cmt.de/archlinux/$repo/os/$arch": True,
                "https://mirror.cmt.de/archlinux/$repo/os/$arch": True,
                "http://os.codefionn.eu/archlinux/$repo/os/$arch": True,
                "https://os.codefionn.eu/archlinux/$repo/os/$arch": True,
                "https://mirror.dogado.de/archlinux/$repo/os/$arch": True,
                "http://mirror.f4st.host/archlinux/$repo/os/$arch": True,
                "https://mirror.f4st.host/archlinux/$repo/os/$arch": True,
                "http://ftp.fau.de/archlinux/$repo/os/$arch": True,
                "https://ftp.fau.de/archlinux/$repo/os/$arch": True,
                "https://pkg.fef.moe/archlinux/$repo/os/$arch": True,
                # "https://dist-mirror.fem.tu-ilmenau.de/archlinux/$repo/os/$arch": True,
                # "http://mirror.fsrv.services/archlinux/$repo/os/$arch": True,
                # "https://mirror.fsrv.services/archlinux/$repo/os/$arch": True,
                # "https://mirror.gnomus.de/$repo/os/$arch": True,
                # "http://www.gutscheindrache.com/mirror/archlinux/$repo/os/$arch": True,
                # "http://ftp.gwdg.de/pub/linux/archlinux/$repo/os/$arch": True,
                "https://archlinux.homeinfo.de/$repo/os/$arch": True,
                "http://archlinux.honkgong.info/$repo/os/$arch": True,
                "http://ftp.hosteurope.de/mirror/ftp.archlinux.org/$repo/os/$arch": True,
                "http://ftp-stud.hs-esslingen.de/pub/Mirrors/archlinux/$repo/os/$arch": True,
                "http://mirror.informatik.tu-freiberg.de/arch/$repo/os/$arch": True,
                "https://mirror.informatik.tu-freiberg.de/arch/$repo/os/$arch": True,
                "http://archlinux.mirror.iphh.net/$repo/os/$arch": True,
                "https://mirror.iusearchbtw.nl/$repo/os/$arch": True,
                "http://mirrors.janbruckner.de/archlinux/$repo/os/$arch": True,
                "https://mirrors.janbruckner.de/archlinux/$repo/os/$arch": True,
                "http://arch.jensgutermuth.de/$repo/os/$arch": True,
                "https://arch.jensgutermuth.de/$repo/os/$arch": True,
                "https://de.arch.mirror.kescher.at/$repo/os/$arch": True,
                "http://mirror.kumi.systems/archlinux/$repo/os/$arch": True,
                "https://mirror.kumi.systems/archlinux/$repo/os/$arch": True,
                "http://mirror.fra10.de.leaseweb.net/archlinux/$repo/os/$arch": True,
                "https://mirror.fra10.de.leaseweb.net/archlinux/$repo/os/$arch": True,
                # "http://mirror.metalgamer.eu/archlinux/$repo/os/$arch": True,
                # "https://mirror.metalgamer.eu/archlinux/$repo/os/$arch": True,
                # "http://mirror.mikrogravitation.org/archlinux/$repo/os/$arch": True,
                # "https://mirror.mikrogravitation.org/archlinux/$repo/os/$arch": True,
                # "http://mirror.lcarilla.de/archlinux/$repo/os/$arch": True,
                # "https://mirror.lcarilla.de/archlinux/$repo/os/$arch": True,
                # "http://mirror.moson.org/arch/$repo/os/$arch": True,
                # "https://mirror.moson.org/arch/$repo/os/$arch": True,
                # "http://mirrors.n-ix.net/archlinux/$repo/os/$arch": True,
                # "https://mirrors.n-ix.net/archlinux/$repo/os/$arch": True,
                # "http://mirror.netcologne.de/archlinux/$repo/os/$arch": True,
                # "https://mirror.netcologne.de/archlinux/$repo/os/$arch": True,
                # "http://mirrors.niyawe.de/archlinux/$repo/os/$arch": True,
                # "https://mirrors.niyawe.de/archlinux/$repo/os/$arch": True,
                # "http://mirror.orbit-os.com/archlinux/$repo/os/$arch": True,
                # "https://mirror.orbit-os.com/archlinux/$repo/os/$arch": True,
                # "http://packages.oth-regensburg.de/archlinux/$repo/os/$arch": True,
                # "https://packages.oth-regensburg.de/archlinux/$repo/os/$arch": True,
                # "http://mirror.pagenotfound.de/archlinux/$repo/os/$arch": True,
                # "https://mirror.pagenotfound.de/archlinux/$repo/os/$arch": True,
                # "http://arch.phinau.de/$repo/os/$arch": True,
                # "https://arch.phinau.de/$repo/os/$arch": True,
                # "https://mirror.pseudoform.org/$repo/os/$arch": True,
                # "https://www.ratenzahlung.de/mirror/archlinux/$repo/os/$arch": True,
                # "https://archlinux.richard-neumann.de/$repo/os/$arch": True,
                # "http://ftp.halifax.rwth-aachen.de/archlinux/$repo/os/$arch": True,
                # "https://ftp.halifax.rwth-aachen.de/archlinux/$repo/os/$arch": True,
                # "http://linux.rz.rub.de/archlinux/$repo/os/$arch": True,
                # "http://mirror.satis-faction.de/archlinux/$repo/os/$arch": True,
                # "https://mirror.satis-faction.de/archlinux/$repo/os/$arch": True,
                # "http://mirror.selfnet.de/archlinux/$repo/os/$arch": True,
                # "https://mirror.selfnet.de/archlinux/$repo/os/$arch": True,
                # "http://ftp.spline.inf.fu-berlin.de/mirrors/archlinux/$repo/os/$arch": True,
                # "https://ftp.spline.inf.fu-berlin.de/mirrors/archlinux/$repo/os/$arch": True,
                # "http://mirror.sunred.org/archlinux/$repo/os/$arch": True,
                # "https://mirror.sunred.org/archlinux/$repo/os/$arch": True,
                # "http://archlinux.thaller.ws/$repo/os/$arch": True,
                # "https://archlinux.thaller.ws/$repo/os/$arch": True,
                # "http://ftp.tu-chemnitz.de/pub/linux/archlinux/$repo/os/$arch": True,
                # "http://mirror.ubrco.de/archlinux/$repo/os/$arch": True,
                # "https://mirror.ubrco.de/archlinux/$repo/os/$arch": True,
                # "http://mirror.undisclose.de/archlinux/$repo/os/$arch": True,
                # "https://mirror.undisclose.de/archlinux/$repo/os/$arch": True,
                # "http://ftp.uni-bayreuth.de/linux/archlinux/$repo/os/$arch": True,
                # "http://ftp.uni-hannover.de/archlinux/$repo/os/$arch": True,
                # "http://ftp.uni-kl.de/pub/linux/archlinux/$repo/os/$arch": True,
                # "http://mirror.united-gameserver.de/archlinux/$repo/os/$arch": True,
                # "https://arch.unixpeople.org/$repo/os/$arch": True,
                # "http://ftp.wrz.de/pub/archlinux/$repo/os/$arch": True,
                # "https://ftp.wrz.de/pub/archlinux/$repo/os/$arch": True,
                # "http://mirror.wtnet.de/archlinux/$repo/os/$arch": True,
                # "https://mirror.wtnet.de/archlinux/$repo/os/$arch": True,
                # "http://mirrors.xtom.de/archlinux/$repo/os/$arch": True,
                # "https://mirrors.xtom.de/archlinux/$repo/os/$arch": True,
                # "http://arch.mirror.zachlge.org/$repo/os/$arch": True,
                # "https://arch.mirror.zachlge.org/$repo/os/$arch": True

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
