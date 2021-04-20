#!/usr/bin/env python3

import argparse
import os
import sys
import textwrap

PROG_NAME = 'add_intended'          # default name
SCRIPT_DIR = 'code'
FMAP_DIR = 'fmap'
FUNC_DIR = 'func'
IMAGE_EXT = '.nii.gz'
PHASEDIFF_EXT = '_phasediff.json'


def main(argv=None):
    """
    --participant_label subj
    --verbose
    """

    # the main method takes no arguments so it can be called by setuptools
    if (argv is None):                      # if called by setuptools
        # then fetch the arguments from the system
        PROG_NAME = sys.argv[0]
        argv = sys.argv[1:]

    # setup command line argument parsing
    parser = argparse.ArgumentParser(
        prog=PROG_NAME,
        formatter_class=argparse.RawTextHelpFormatter,
        description=f"{PROG_NAME}: Adds 'IntendedFor' array to the phasediff JSON sidecars for one or more subjects."
    )

    # add optional arguments
    parser.add_argument(
        '--participant_label', '--participant-label', dest='subjnum',
        default=argparse.SUPPRESS,
        help=textwrap.dedent("(Optional) Subject number to process [default: process all subjects]")
    )

    # set verbosity
    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true',
        default=False,
        help='Print informational messages during processing [default: False (non-verbose mode)].'
    )

    # actually parse the arguments now from the command line
    args = vars(parser.parse_args(argv))

    # if debugging, set verbose and echo input arguments
    if (args.get('verbose')):
        print(f"({PROG_NAME}): arguments={args}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python version: {sys.version}")



if __name__ == "__main__":
    main()
