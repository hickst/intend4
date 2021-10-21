#!/usr/bin/env python3
#
# Program to create IntendedFor array in phasediff JSON sidecar files in order
# to trigger fMRIPrep to run SDC (Susceptibility Distortion Correction).
#   Written by: Tom Hicks and Dianne Patterson. 4/21/21.
#   Last Modified: Continue enhancing: add new arguments, checking, and status messages.
#
import argparse
import os
import sys
import textwrap

import intend4.intend4 as in4
from intend4 import ALLOWED_MODALITIES
from intend4.file_utils import good_dir_path


BIDS_DIR_EXIT_CODE = 10
PROG_NAME = 'intend4'                  # program name


def check_bids_dir (program_name, bids_dir):
  """
  Check that the BIDS data directory is a writeable directory.
  If unable to find or write to the directory, then exit out.
  """
  if (not good_dir_path(bids_dir, writeable=True)):
      helpMsg =  "A writeable BIDS data directory must be specified."
      errMsg = "({}): ERROR: {} Exiting...".format(program_name, helpMsg)
      print(errMsg, file=sys.stderr)
      sys.exit(BIDS_DIR_EXIT_CODE)


def main(argv=None):
  """
  --bids_dir directory
  --participant_label subj
  --verbose
  """

  # the main method takes no arguments so it can be called by setuptools
  if (argv is None):                   # if called by setuptools
    argv = sys.argv[1:]                # then fetch the arguments from the system

  # setup command line argument parsing
  parser = argparse.ArgumentParser(
    prog=PROG_NAME,
    formatter_class=argparse.RawTextHelpFormatter,
    description=f"{PROG_NAME}: Adds or removes 'IntendedFor' info to the JSON sidecars, for one or more subjects."
  )

  # set verbosity
  parser.add_argument(
    '-v', '--verbose', dest='verbose', action='store_true',
    default=False,
    help='Print informational messages during processing [default: False (non-verbose mode)].'
  )

  parser.add_argument(
    'modality', choices=ALLOWED_MODALITIES, 
    help=f"Modality of the image files. Must be one of: {ALLOWED_MODALITIES}"
  )

  parser.add_argument(
    '--bids_dir', dest='bids_dir',
    default=argparse.SUPPRESS,
    help=textwrap.dedent("(Optional) Path to BIDS data directory [default: current directory]")
  )

  # add optional arguments
  parser.add_argument(
    '--participant_label', '--participant-label', dest='subj_ids',
    nargs='*', default=argparse.SUPPRESS,
    help=textwrap.dedent("(Optional) Space-separated subject number(s) to process [default: process all subjects]")
  )

  parser.add_argument(
    '--remove', dest='remove', action='store_true',
    default=False,
    help='REMOVE IntendedFor entries for the selected modality [default: False].'
  )

  # actually parse the arguments now from the command line
  args = vars(parser.parse_args(argv))

  # check modality for validity: assumes arg parse provides valid value
  modality = in4.validate_modality(args.get('modality'))

  # check that the given BIDS dir exists and is writeable
  bids_dir = args.get('bids_dir', os.getcwd())
  check_bids_dir(PROG_NAME, bids_dir)

  snums = args.get('subj_ids')
  if (snums is not None and not snums):    # only True if snums is an empty list
    sys.exit('Error: if --participant_label is used, one or more subject numbers must be specified.')

  # # For debugging: set verbose and echo input arguments
  if (args.get('verbose')):
    print(f"({PROG_NAME}): arguments={args}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")

  if (args.get('verbose')):
    print(f"({PROG_NAME}): Modifying sidecar files for modality '{modality}'.",
      file=sys.stderr)

  # do the specified sidecar modifications
  mod_count = in4.do_subjects(args)

  if (args.get('verbose')):
    print(f"({PROG_NAME}): Modified {mod_count} sidecars.")



if __name__ == "__main__":
  main()
