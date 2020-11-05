# -*- coding: utf-8 -*-
# FSegerer 26072020

# helper functions for backmeup tool

from pathlib import Path
import shutil
import time
import csv


def progress(count, total, suffix=''):
    """

    :param count:
    :param total:
    :param suffix:
    """
    bar_len = 20
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    print('\r [%s] %s%s %s' % (bar, percents, '% ', suffix), flush=True, end=' ')


def conditional_copy(path_source, path_dest, dry_run=False):
    """

    :param dry_run:
    :param path_source:
    :param path_dest:
    """
    if not path_dest.exists():
        print(f' - copying {str(path_source)}', flush=True)

        if not dry_run:
            path_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path_source, path_dest)
        return 1
    elif (path_source.stat().st_mtime -
          path_dest.stat().st_mtime) > 1:
        print(f' - updating from {str(path_source)}', flush=True)

        if not dry_run:
            path_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path_source, path_dest)
        return 1
    else:
        return 0


def conditional_delete(path_source, path_dest, list_source, dry_run=False):
    """

    :param path_source:
    :param path_dest:
    :param list_source:
    :param dry_run:
    :return:
    """
    if path_source not in list_source:
        if path_dest.is_dir():
            print(f' - deleting dir {str(path_dest)}', flush=True)
            if not dry_run:
                shutil.rmtree(str(path_dest))
        else:
            filename = path_dest.name
            print(f' - deleting {filename}', flush=True)
            if not dry_run:
                path_dest.unlink()
        return 1
    else:
        return 0


def list_filedirs(dir_source):
    """

    :param dir_source:
    :return:
    """
    if isinstance(dir_source, str):
        dir_source = Path(dir_source)

    list_files = []
    list_dirs = []

    for cur_file in dir_source.rglob("*"):
        if not cur_file.is_dir():
            list_files.append(cur_file)
        else:
            list_dirs.append(cur_file)

    return list_files, list_dirs


def backup_dir(dir_source, dir_dest, delete=False, dry_run=False):
    """

    :param delete:
    :param dir_source:
    :param dir_dest:
    :param dry_run:
    :return:
    """
    if isinstance(dir_source, str):
        dir_source = Path(dir_source)
    if isinstance(dir_dest, str):
        dir_dest = Path(dir_dest)

    print(f'Backing up files in {dir_source} in {dir_dest}.')

    list_files_source, list_dirs_source = list_filedirs(dir_source)
    # initialize stats
    num_checked = len(list_files_source)
    num_copied = 0
    num_deleted = 0

    cur_num_file = 1
    for cur_file in list_files_source:
        cur_dest = Path(str(cur_file).replace(str(dir_source), str(dir_dest)))
        num_copied += conditional_copy(cur_file,
                                       cur_dest,
                                       dry_run=dry_run)
        progress(cur_num_file, num_checked, suffix='of files checked')
        cur_num_file += 1

    if delete:
        print('All files stored, checking for files to delete now.')
        list_files_dest, list_dirs_dest = list_filedirs(dir_dest)

        num_dest = len(list_files_dest)
        cur_num_file = 1
        for cur_file_dest in list_files_dest:
            cur_file_source = Path(str(cur_file_dest).replace(str(dir_dest), str(dir_source)))
            num_deleted += conditional_delete(cur_file_source, cur_file_dest, list_files_source, dry_run=dry_run)
            progress(cur_num_file, num_dest, suffix='of files checked')
            cur_num_file += 1

        for cur_dir_dest in list_dirs_dest:
            cur_dir_source = Path(str(cur_dir_dest).replace(str(dir_dest), str(dir_source)))
            conditional_delete(cur_dir_source, cur_dir_dest, list_dirs_source, dry_run=dry_run)

    print(f'\nStored {num_copied} files out of {num_checked} from \"{dir_source}\".'
          f'\nDeleted {num_deleted} files in destination directory.')


def backmeup(dir_source=None, dir_dest=None, cfg_table=None, delete=False, dry_run=False):
    """

    :param delete:
    :param dir_source:
    :param dir_dest:
    :param cfg_table:
    :param dry_run:
    """
    assert not (cfg_table and dir_source or cfg_table and dir_dest), \
        'Paths provided in config table and as parameters. ' \
        'You\'ll have to decide for one option I am afraid.'
    time_start = time.time()

    if cfg_table:
        # check_cfg_format(cfg_table)
        with open(cfg_table, newline='\n') as cfg_file:
            reader = csv.DictReader(cfg_file, fieldnames=['source_dir', 'dest_dir'])
            # skip header row
            next(reader)
            for row in reader:
                source_dir = row['source_dir']
                dest_dir = row['dest_dir']
                print(f'Backing up files in {source_dir} in {dest_dir}.')
                backup_dir(source_dir,
                           dest_dir,
                           delete=delete,
                           dry_run=dry_run)
    else:
        backup_dir(dir_source,
                   dir_dest,
                   delete=delete,
                   dry_run=dry_run)
    time_end = time.time()
    time_run = (time_end - time_start) / 60
    print(f"Hurray! All files backed up in only {time_run:5.2f} minutes")
