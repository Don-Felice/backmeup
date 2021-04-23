# -*- coding: utf-8 -*-
# FSegerer 26072020

# Backup folders and files

from backmeup.utils import backmeup
from backmeup.args import get_args


def main():
    args = get_args()

    backmeup(dir_source=args.source_dir,
             dir_dest=args.dest_dir,
             cfg_table=args.cfg_file,
             delete=args.delete,
             dry_run=args.dry_run)


if __name__ == '__main__':
    main()
