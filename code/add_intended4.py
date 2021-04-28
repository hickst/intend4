#!/usr/bin/env python3
#
# Program to create IntendedFor array in phasediff JSON sidecar files in order
# to trigger fMRIPrep to run SDC (Susceptibility Distortion Correction).
# Written by: Tom Hicks and Dianne Patterson. 4/21/21.

import argparse
import os
import sys
import bids
import json
import textwrap
from bids import BIDSLayout

PROG_NAME = 'add_intended4'          # default name
FMAP_DIR = 'fmap'
IMAGE_EXT = ['nii.gz', 'nii']
PHASEDIFF_EXT = 'json'
PHASEDIFF_SUFFIX = 'phasediff'
SUBJ_DIR_PREFIX = 'sub-'


def has_session(layout, subj_id):
    return subj_id in layout.get(return_type='id', target='subject', session=layout.get_sessions())


def sessions_for_subject(layout, subj_id):
    return layout.get(return_type='id', target='session', subject=subj_id)

def insert_intended_for (args, layout, fmri_image_paths, pd_sidecar):
    # print(f"(insert_intended_for): args={args}, paths={fmri_image_paths}, sidecar={pd_sidecar}")  # REMOVE LATER
    pd_dict = pd_sidecar.get_dict()
    pd_dict['IntendedFor'] = fmri_image_paths
    return pd_dict


def get_sidecar_and_insert (args, layout, fmri_image_paths, subj_id, session_id=None):
    print(f"\n(get_sidecar_and_insert): args={args}, SUBJ={subj_id}, SESS={session_id}")  # REMOVE LATER
    print(f"(get_sidecar_and_insert): PATHS={fmri_image_paths}")  # REMOVE LATER
    pd_sidecars = layout.get(target='subject', subject=subj_id, session=session_id,
        suffix=PHASEDIFF_SUFFIX, extension=PHASEDIFF_EXT)
    print(f"(get_sidecar_and_insert): PDCARS={pd_sidecars}")  # REMOVE LATER

    num_sidecars = len(pd_sidecars)
    if (num_sidecars < 1):
        sess = f" in session {session_id}" if session_id else ''
        err_msg = f"Error: {PHASEDIFF_SUFFIX} sidecar file is missing for subject {subj_id}{sess}. Skipping..."
        print(err_msg, file=sys.stderr)
        return
    elif (num_sidecars > 1):
        sess = f" in session {session_id}" if session_id else ''
        err_msg = f"Error: Found more than 1 {PHASEDIFF_SUFFIX} sidecars for subject {subj_id}{sess}. Skipping..."
        print(err_msg, file=sys.stderr)
        return
    else:
        modified_dict = insert_intended_for(args, layout, fmri_image_paths, pd_sidecars[0])
        print(modified_dict)        # REMOVE LATER
        # TODO: convert modified dictionary to JSON and write back to sidecar file


def get_fmri_image_paths (args, layout, subj_id, session_id=None):
    files = layout.get(subject=subj_id, session=session_id, extension=IMAGE_EXT, suffix='bold')
    return [subjrelpath(fyl) for fyl in files]


def update_phasediff_fmaps(args, layout, subj_id, session_id=None):
    fmri_image_paths = get_fmri_image_paths(args, layout, subj_id, session_id=session_id)
    if (fmri_image_paths):
        get_sidecar_and_insert(args, layout, fmri_image_paths, subj_id, session_id=session_id)
 

def do_single_subject(args, layout, subj_id):
    # print(f"(do_single_subject): args={args}, SUBJ={subj_id}") # REMOVE LATER
    sessions = sessions_for_subject(layout, subj_id)
    if (sessions):      # if there are sessions in use
        for sess_num in sessions:
            update_phasediff_fmaps(args, layout, subj_id, session_id=sess_num)
    else:               # else sessions are not being used
        update_phasediff_fmaps(args, layout, subj_id)


def do_subjects(args):
    # use the optionally specified BIDS data dir or default to current directory
    bids_dir = args.get('bids_dir', os.getcwd())

    # following setting avoids an annoying warning message about deprecated feature
    bids.config.set_option('extension_initial_dot', True)
    layout = BIDSLayout(bids_dir, validate=False)

    # use the optionally specified list of subjects or default to all subjects
    subj_ids = args.get('subj_ids')
    if (subj_ids is not None):
        selected_subjects = subj_ids
    else:
        selected_subjects = layout.get_subjects()
    ## args['selected_subjects'] = selected_subjects  # USE or REMOVE LATER?
    for subj_id in selected_subjects:
        do_single_subject(args, layout, subj_id)


def subjrelpath(bids_file_object):
    """
    Return the subject-relative path for the given BIDSFile or None if the
    given file is not a relative to any subject.
    """
    relpath = bids_file_object.relpath
    if (relpath.startswith(SUBJ_DIR_PREFIX)):
        ndx = relpath.find('/')
        if (ndx != -1):
            return relpath[ndx+1:]
        else:
            raise TypeError(f"Error: Unable to remove subject prefix from {relpath}: no '/' found.")
    else:           # given file is not relative to a subject directory
        return None


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

    # if debugging, set verbose and echo input arguments
    if (args.get('verbose')):
        print(f"({PROG_NAME}): arguments={args}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python version: {sys.version}")

    # do the work for each subject
    do_subjects(args)



if __name__ == "__main__":
    main()
