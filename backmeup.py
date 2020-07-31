# -*- coding: utf-8 -*-
# FSegerer 26072020

# Backup folders and files

# generic imports
from pathlib import Path
import argparse

# project intern imports
from backmeup.utils import backmeup



if __name__ == "__main__":
    #TODO
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source_dir", type=str, default=None,
                        help="source directory")
    parser.add_argument("-d", "--dest_dir", type=str, default=None,
                        help="destination directory")
    parser.add_argument("-cfg", "--cfg_file", type=str, default=None,
                        help="destination directory")
    parser.add_argument("-dr", "--dry_run", action='store_true', default=False,
                        help="destination directory")

    args = parser.parse_args()

    backmeup(dir_source=args.source_dir, dir_dest=args.dest_dir, cfg_table=args.cfg_file, dry_run=args.dry_run)