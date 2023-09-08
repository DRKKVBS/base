import os
import pwd
import shutil


def copy_recursive(copy_src: str, copy_dst: str, dir_mode: int, ownership: tuple, ignore: list):
    """ Copy a Directory recursively, replacing old files and creating new directories if necessary. """

    if os.path.isfile(copy_src):
        shutil.copyfile(copy_src)

    if not os.path.exists(copy_dst):
        os.makedirs(copy_dst, mode=dir_mode)

    for root_dir, _, file_names in os.walk(copy_src, topdown=True):
        new_root_dir = os.path.join(root_dir.replace(copy_src, copy_dst))
        print('New Root Dir:...', new_root_dir)
        print('New Root Dir:...', os.path.exists(new_root_dir))
        uid = pwd.getpwnam(ownership[0]).pw_uid
        gid = pwd.getpwnam(ownership[1]).pw_gid
        if not os.path.exists(new_root_dir):
            print('Creating new directories for: ', new_root_dir)
            os.mkdir(new_root_dir, mode=dir_mode)
            print('Created...', new_root_dir)
            os.chown(new_root_dir, uid=uid, gid=gid)
        for file in file_names:
            if len(ignore) > 0 and file in ignore:
                continue
            #print('Copy file: ', file, ' to ', new_root_dir)
            shutil.copyfile(os.path.join(root_dir, file),
                            os.path.join(new_root_dir, file))
            os.chown(os.path.join(new_root_dir, file), uid=uid, gid=gid)


def merge_and_update_dicts(dict1: dict, dict2: dict):
    """ Merge two json files. Extending lists and dictonaries and update values."""
    for k, v in dict1.items():
        if type(v) == list:
            dict2[k].extend(v)
            temp_lst = list(dict.fromkeys(dict2[k]))
            dict2[k].clear()
            dict2[k].extend(temp_lst)
            dict2[k].sort()
        elif type(v) == dict:
            dict2[k] = merge_and_update_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict2
