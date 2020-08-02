# -*- coding: utf-8 -*-
# FSegerer 26072020

# test folder backup

from ..backmeup.utils import backmeup
from pathlib import Path
import shutil
import os


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
    assert os.path.getmtime(file1) - os.path.getmtime(file2) <= 1, \
        f'File modification time is not consistent for file {file1}'


def test_backup():
    path_cfg_template = Path(__file__).parent / 'cfg_template.csv'

    # create temporary test data
    path_testrun = Path(__file__).parent / 'temp_testrun'
    path_testrun.mkdir(parents=True)

    shutil.copytree(Path(__file__).parent / 'data', path_testrun / 'data')

    path_cfg_test = create_test_cfg(path_cfg_template, path_testrun)

    # run the actual function
    backmeup(cfg_table=path_cfg_test)
    print('Backup went through.')
    # copmare files
    list_dirs = [[path_testrun / 'data' / 'dir_source_1', path_testrun / 'data' / 'dir_dest_1'],
                 [path_testrun / 'data' / 'dir_source_2', path_testrun / 'data' / 'dir_dest_2']]
    try:
        for dir_pair in list_dirs:
            dir_source, dir_dest = dir_pair
            print('---------------------')
            print(f'checking consistencies of folders:\n{str(dir_source)}\nand\n{str(dir_dest)}.')
            list_files_source = [x for x in dir_source.rglob("*") if not x.is_dir()]
            for cur_file_source in list_files_source:
                cur_file_dest = Path(str(cur_file_source).replace(str(dir_source), str(dir_dest)))
                print(f'checking file {cur_file_source}')
                # check for existence
                assert cur_file_dest.exists(), \
                    f'file {cur_file_source} not properly copied to dest dir.'
                # check for proper updating
                check_mtime_consistency(cur_file_source, cur_file_dest)
    finally:
        # clean stuff up
        shutil.rmtree(path_testrun)
