import os
import pwd
import shutil


def copy_recursive(copy_src: str, copy_dst: str, dir_mode: int, ownership: tuple, ignore: list):
    """ Copy a Directory recursively, replacing old files and creating new directories if necessary. """

    for dir_path, dir_names, file_names in os.walk(copy_src, topdown=True):

        uid = pwd.getpwnam(ownership[0]).pw_uid
        gid = pwd.getpwnam(ownership[1]).pw_gid

        for dir in dir_names:
            path = os.path.join(copy_dst, dir)
            print('Path: ', os.path.join(path, dir))
            if not os.path.exists(os.path.join(path, dir)):
                print('Creating new directories for: ', os.path.join(path, dir))
                os.makedirs(os.path.join(path, dir), mode=dir_mode)
                shutil.chown(os.path.join(path, dir),
                             uid=uid, gid=gid)
        for file in file_names:
            if len(ignore) > 0 and file in ignore:
                continue
            print('Copy file: ', file, ' to ', path)
            shutil.copyfile(os.path.join(dir_path, file),
                            os.path.join(path, file))
            shutil.chown(os.path.join(path, file),
                         uid=uid, gid=gid)


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
