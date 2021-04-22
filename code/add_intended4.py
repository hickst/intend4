#!/usr/bin/env python3
#
# Program to create IntendedFor array in phasediff JSON sidecar files in order
# to trigger fMRIPrep to run SDC (Susceptibility Distortion Correction).
# Written by: Tom Hicks and Dianne Patterson. 4/21/21.

import argparse
import os
import sys
import textwrap
import bids
from bids import BIDSLayout

PROG_NAME = 'add_intended'          # default name
FMAP_DIR = 'fmap'
FUNC_DIR = 'func'
IMAGE_EXT = '.nii.gz'
PHASEDIFF_EXT = '_phasediff.json'
SUBJ_DIR_PREFIX = 'sub-'


def do_single_subject(args, layout, subjnum):
    print(f"(d_s_s): args={args}, SUBJ={subjnum}")


def do_subjects(args):
    # use the optionally specified BIDS data dir or default to current directory
    bids_dir = args.get('bids_dir', os.getcwd())

    # following setting avoids an annoying warning message about deprecated feature
    bids.config.set_option('extension_initial_dot', True)
    layout = BIDSLayout(bids_dir, validate=False)

    # use the optionally specified subject or default to all subjects
    subjnum = args.get('subjnum')
    if (subjnum is not None):
        do_single_subject(args, layout, subjnum)
    else:
        for subjnum in layout.get_subjects():
            do_single_subject(args, layout, subjnum)


def main(argv=None):
    """
    --bids_dir directory
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

    parser.add_argument(
        '--bids_dir', dest='bids_dir',
        default=argparse.SUPPRESS,
        help=textwrap.dedent("(Optional) Path to BIDS data directory [default: current directory]")
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

    # do the work for each subject
    do_subjects(args)



if __name__ == "__main__":
    main()
