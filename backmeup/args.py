# -*- coding: utf-8 -*-
# FSegerer 26072020

import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source_dir", type=str, default=None,
                        help="source directory")
    parser.add_argument("-d", "--dest_dir", type=str, default=None,
                        help="destination directory")
    parser.add_argument("-cfg", "--cfg_file", type=str, default=None,
                        help="destination directory")
    parser.add_argument("-del", "--delete", action='store_true', default=False,
                        help="delete files which exist in destination directory but not in the source directory")
    parser.add_argument("-dr", "--dry_run", action='store_true', default=False,
                        help="destination directory")

    args = parser.parse_args()

    return args
