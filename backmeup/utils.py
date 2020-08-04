# -*- coding: utf-8 -*-
# FSegerer 26072020

# helper functions for backmeup tool

from pathlib import Path
import os
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
            os.makedirs(os.path.dirname(str(path_dest)), exist_ok=True)
            shutil.copy2(path_source, path_dest)
        return 1
    elif (os.path.getmtime(str(path_source)) -
          os.path.getmtime(str(path_dest))) > 1:
        filename = path_source.name
        sys.stdout.write(f' - updating {filename}')
        sys.stdout.flush()

        if not dry_run:
            os.makedirs(os.path.dirname(str(path_dest)), exist_ok=True)
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

    list_files = [str(x) for x in dir_source.rglob("*") if not x.is_dir()]
    return list_files


def backup_dir(dir_source, dir_dest, dry_run=False):
    """

    :param dir_source:
    :param dir_dest:
    :param dry_run:
    :return:
    """
    if isinstance(dir_source, str):
        dir_source = Path(dir_source)
    if isinstance(dir_dest, str):
        dir_dest = Path(dir_dest)

    list_files_source = list_filedirs(dir_source)
    # initialize stats
    num_checked = len(list_files_source)
    num_copied = 0

    cur_num_file = 1
    for cur_file in list_files_source:
        num_copied += \
            conditional_copy(Path(cur_file),
                             Path(str(cur_file).replace(str(dir_source),
                             str(dir_dest))),
                             dry_run=dry_run)
        progress(cur_num_file, num_checked, suffix='of files checked')
        cur_num_file += 1
    num_ignored = num_checked - num_copied

    return num_checked, num_copied, num_ignored


def backmeup(dir_source=None, dir_dest=None, cfg_table=None, dry_run=False):
    """

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
                num_checked, num_updated, num_ignored = \
                    backup_dir(source_dir,
                               dest_dir,
                               dry_run=dry_run)
                print(f'\n Stored {num_updated} files '
                      f'from {num_checked} in {source_dir}.')
    else:
        print(f'Backing up files in {dir_source} in {dir_dest}.')
        num_checked, num_updated, num_ignored = backup_dir(dir_source,
                                                           dir_dest,
                                                           dry_run=dry_run)
        print(f'Stored {num_updated} files '
              f'from {num_checked} in {dir_source}.')
    time_end = time.time()
    time_run = (time_end - time_start) / 60
    print(f"Hurray! All files backed up in only {time_run:5.2f} minutes")
