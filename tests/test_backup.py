# -*- coding: utf-8 -*-
# FSegerer 26072020

# test folder backup

from ..backmeup.utils import backmeup
from pathlib import Path
import shutil
import os
import pytest


def create_test_cfg(path_cfg, path_output):
    if isinstance(path_cfg, str):
        path_cfg = Path(path_cfg)
    if isinstance(path_output, str):
        path_output = Path(path_output)

    with path_cfg.open('r') as file:
        text_cfg = file.read()

    text_cfg = text_cfg.replace("WHEREAMI", str(path_output))

    path_output = path_output / path_cfg.name
    with path_output.open('w') as file:
        file.write(text_cfg)
    return path_output


def check_mtime_consistency(file1, file2):
    assert abs(os.path.getmtime(file1) - os.path.getmtime(file2)) <= 1, \
        f'File modification time is not consistent for file {file1}'


def compare_files(dir_source, dir_ref):
    print('---------------------')
    print(
        f'checking consistencies of folders:'
        f'\n{str(dir_source)}\nand\n{str(dir_ref)}.')
    list_files_source = [x for x in dir_source.rglob("*") if
                         not x.is_dir()]
    for cur_file_source in list_files_source:
        cur_file_dest = Path(
            str(cur_file_source).replace(str(dir_source), str(dir_ref)))
        print(f'checking file {cur_file_source}')
        # check for existence
        assert cur_file_dest.exists(), \
            f'file {cur_file_source} not properly copied to dest dir.'
        # check for proper updating
        check_mtime_consistency(cur_file_source, cur_file_dest)
    print('---------------------')


@pytest.yield_fixture(scope='function')
def dir_testrun():
    # create temporary test data
    path_testrun = Path(__file__).parent / 'temp_testrun'
    path_testrun.mkdir(parents=True)

    # create source dest structure for update test
    shutil.copytree(Path(__file__).parent / 'data', path_testrun / 'data')

    # update some files to change mtime
    path_updateme = path_testrun / 'data' / 'dir_source_1' / 'subdir_1' / 'subsubdir_1' / 'L3_file_1.txt'
    with path_updateme.open('a') as filetoupdate:
        filetoupdate.write('I have been updated.')

    # create source reference for check source dir integrity
    shutil.copytree(path_testrun / 'data' / 'dir_source_1', path_testrun / 'data' / 'dir_source_1_ref')
    shutil.copytree(path_testrun / 'data' / 'dir_source_2', path_testrun / 'data' / 'dir_source_2_ref')

    try:
        yield path_testrun

    finally:
        # cleanup stuff
        shutil.rmtree(path_testrun)
        print('Test Done')


@pytest.fixture(scope='function')
def list_dirs(dir_testrun, num_dirs=2):
    list_dirs_sourdest = [[dir_testrun / 'data' / ('dir_source_' + str(i + 1)),
                           dir_testrun / 'data' / ('dir_dest_' + str(i + 1))] for i in
                          range(num_dirs)]
    list_dirs_sourref = [[dir_testrun / 'data' / ('dir_source_' + str(i + 1)),
                          dir_testrun / 'data' / ('dir_source_' + str(i + 1) + '_ref')] for i in
                         range(num_dirs)]
    return [list_dirs_sourdest, list_dirs_sourref]


@pytest.fixture(scope='function')
def cfg_testrun(dir_testrun):
    path_cfg_template = Path(__file__).parent / 'cfg_template.csv'
    path_cfg_test = create_test_cfg(path_cfg_template, dir_testrun)
    return path_cfg_test


def test_backup_cfg(cfg_testrun, list_dirs):
    # run the actual function to test
    backmeup(cfg_table=cfg_testrun)
    print('Backup went through.')

    # check for proper updating
    for dir_pair in list_dirs[0]:
        dir_source, dir_dest = dir_pair
        compare_files(dir_source, dir_dest)

    # check for source dir integrity
    for dir_pair in list_dirs[1]:
        dir_source, dir_source_ref = dir_pair
        compare_files(dir_source, dir_source_ref)


def test_backup_indi(list_dirs):
    # check for proper updating
    for dir_pair in list_dirs[0]:
        dir_source, dir_dest = dir_pair
        # run the actual function to test
        backmeup(dir_source=str(dir_source), dir_dest=str(dir_dest))
        print(f'Individual backup went through for {dir_source}.')
        # compare files
        compare_files(dir_source, dir_dest)

    # check for source dir integrity
    for dir_pair in list_dirs[1]:
        dir_source, dir_source_ref = dir_pair
        compare_files(dir_source, dir_source_ref)
