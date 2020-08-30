# -*- coding: utf-8 -*-
# FSegerer 26072020

# helper functions for backmeup tool

from pathlib import Path
import shutil
import sys
import time
import csv


def progress(count, total, suffix=''):
    bar_len = 20
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('\r [%s] %s%s %s' % (bar, percents, '% ', suffix))
    sys.stdout.flush()


def conditional_copy(path_source, path_dest, dry_run=False):
    """

    :param dry_run:
    :param path_source:
    :param path_dest:
    """
    if not path_dest.exists():
        filename = path_source.name
        sys.stdout.write(f' - copying {filename}')
        sys.stdout.flush()

        if not dry_run:
            path_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path_source, path_dest)
        return 1
    elif (path_source.stat().st_mtime -
          path_dest.stat().st_mtime) > 1:
        filename = path_source.name
        sys.stdout.write(f' - updating {filename}')
        sys.stdout.flush()

        if not dry_run:
            path_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path_source, path_dest)
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
    num_ignored = num_checked - num_copied

    if delete:
        print('All files stored, checking for files to delete.')
        list_files_dest, list_dirs_dest = list_filedirs(dir_dest)

        num_dest = len(list_files_dest)
        cur_num_file = 1
        for cur_file_dest in list_files_dest:
            cur_file_source = Path(str(cur_file_dest).replace(str(dir_dest), str(dir_source)))
            if cur_file_source not in list_files_source:
                filename = cur_file_dest.name
                sys.stdout.write(f' - deleting {filename}')
                sys.stdout.flush()

                if not dry_run:
                    cur_file_dest.unlink()

                num_deleted += 1
            progress(cur_num_file, num_dest, suffix='of files checked')
            cur_num_file += 1

        for cur_dir_dest in list_dirs_dest:
            cur_dir_source = Path(str(cur_dir_dest).replace(str(dir_dest), str(dir_source)))
            if cur_dir_source not in list_dirs_source:
                sys.stdout.write(f' - deleting dir {str(cur_dir_dest)}')
                sys.stdout.flush()
                cur_dir_dest.rmdir()

    return num_checked, num_copied, num_ignored, num_deleted


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
            reader = csv.DictReader(cfg_file,
                                    fieldnames=['source_dir', 'dest_dir'])
            # skip header row
            next(reader)
            for row in reader:
                source_dir = row['source_dir']
                dest_dir = row['dest_dir']
                print(f'Backing up files in {source_dir} in {dest_dir}.')
                num_checked, num_updated, num_ignored, num_deleted = \
                    backup_dir(source_dir,
                               dest_dir,
                               delete=delete,
                               dry_run=dry_run)
                print(f'\n Stored {num_updated} files '
                      f'from {num_checked} from {source_dir}. '
                      f'Deleted {num_deleted} files in destination directory')
    else:
        print(f'Backing up files in {dir_source} in {dir_dest}.')
        num_checked, num_updated, num_ignored, num_deleted = backup_dir(dir_source,
                                                                        dir_dest,
                                                                        delete=delete,
                                                                        dry_run=dry_run)
        print(f'Stored {num_updated} files '
              f'from {num_checked} in {dir_source}. '
              f'Deleted {num_deleted} files in destination directory')

    time_end = time.time()
    time_run = (time_end - time_start) / 60
    print(f"Hurray! All files backed up in only {time_run:5.2f} minutes")
