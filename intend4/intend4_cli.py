#!/usr/bin/env python3
#
# Program to create IntendedFor array in phasediff JSON sidecar files in order
# to trigger fMRIPrep to run SDC (Susceptibility Distortion Correction).
#   Written by: Tom Hicks and Dianne Patterson. 4/21/21.
#   Last Modified: Separate into CLI and lib modules.
#
import argparse
import os
import sys
import textwrap

from intend4.intend4 import do_subjects


PROG_NAME = 'intended4'                # program name
FMAP_DIR = 'fmap'
IMAGE_EXT = ['nii.gz', 'nii']
PHASEDIFF_EXT = 'json'
PHASEDIFF_SUFFIX = 'phasediff'
SUBJ_DIR_PREFIX = 'sub-'


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
    '--participant_label', '--participant-label', dest='subj_ids',
    nargs='*', default=argparse.SUPPRESS,
    help=textwrap.dedent("(Optional) Space-separated subject number(s) to process [default: process all subjects]")
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

  # check any validate any arguments that need it
  snums = args.get('subj_ids')
  if (snums is not None and not snums):    # only True if snums is an empty list
    sys.exit('Error: if --participant_label is used, one or more subject numbers must be specified.')

  # # For debugging: set verbose and echo input arguments
  if (args.get('verbose')):
    print(f"({PROG_NAME}): arguments={args}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")

  # do the work for each subject
  do_subjects(args)



if __name__ == "__main__":
  main()
