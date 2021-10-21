# Program to insert IntendedFor array in phasediff JSON sidecar files in order
# to trigger fMRIPrep to run SDC (Susceptibility Distortion Correction).
#   Written by: Tom Hicks and Dianne Patterson. 4/21/21.
#   Last Modified: Move get_permission out, add validate_modality.
#
import os
import sys
import bids
import json
from bids import BIDSLayout

from intend4 import ALLOWED_MODALITIES
from intend4.file_utils import get_permissions


IMAGE_EXT = ['nii.gz', 'nii']
PHASEDIFF_SUFFIX = 'phasediff'
SIDECAR_EXT = 'json'
SUBJ_DIR_PREFIX = 'sub-'


def do_subjects(args):
  """
  Find and modify all phase diff sidecars for the specified (or all) subjects
  and sessions.
  """
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
  for subj_id in selected_subjects:
    do_single_subject(args, layout, subj_id)


def do_single_subject(args, layout, subj_id):
  """
  Find and modify the phase diff sidecars for a single subject (and optional sessions).
  """
  sessions = sessions_for_subject(layout, subj_id)
  if (sessions):             # if there are sessions in use
    for sess_num in sessions:
      update_phasediff_fmaps(args, layout, subj_id, session_id=sess_num)
  else:                      # else sessions are not being used
    update_phasediff_fmaps(args, layout, subj_id)


def get_fmri_image_paths (args, layout, subj_id, session_id=None):
  """
  Return a list of fMRI image paths for the given subject (or subject/session).
  """
  files = layout.get(subject=subj_id, session=session_id, extension=IMAGE_EXT, suffix='bold')
  return [subjrelpath(fyl) for fyl in files]


def get_sidecar_and_insert (args, layout, fmri_image_paths, subj_id, session_id=None):
  """
  Insert the given fMRI image paths into the appropriate sidecar data structure for
  for identified subject (or subject/session). Then rewrite the (modified) sidecar.
  Raise an error if more than one sidecar is found per subject (or subject/session).
  """
  pd_sidecars = layout.get(target='subject', subject=subj_id, session=session_id,
                           suffix=PHASEDIFF_SUFFIX, extension=SIDECAR_EXT)
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
    pd_sidecar = pd_sidecars[0]
    modified_sidecar = insert_intended_for(args, fmri_image_paths, pd_sidecar)
    write_intended_for(args, modified_sidecar, pd_sidecar)


def has_session(layout, subj_id):
  "Tell whether the identified subject has sessions or not."
  return subj_id in layout.get(return_type='id', target='subject', session=layout.get_sessions())


def insert_intended_for (args, fmri_image_paths, pd_sidecar):
  """
  Modify the sidecar data structure, storing the fMRI image paths under
  the IntendedFor key. If IntendedFor key already exists, its contents
  are replaced by the given fMRI image paths.
  Returns the sidecar data structure sorted by keywords.
  """
  pd_dict = pd_sidecar.get_dict()
  pd_dict['IntendedFor'] = fmri_image_paths
  sorted_dict = dict(sorted(pd_dict.items()))
  return sorted_dict


def output_JSON (data, file_path=None, **json_keywords):
  """
  Jsonify and write the given data structure to the given file path,
  standard output, or standard error.
  """
  if ((file_path is None) or (file_path == sys.stdout)):  # if writing to standard output
    json.dump(data, sys.stdout, indent=2, **json_keywords)
    sys.stdout.write('\n')
  else:                               # else file path was given
    outfile = open(file_path, 'w')
    json.dump(data, outfile, indent=2, **json_keywords)
    outfile.write('\n')
    outfile.close()


def sessions_for_subject(layout, subj_id):
  "Return a list of session IDs for the identified subject."
  return layout.get(return_type='id', target='session', subject=subj_id)


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
  else:                                # given file is not relative to a subject directory
    return None


def update_phasediff_fmaps(args, layout, subj_id, session_id=None):
  """
  Get paths to all fMRI images for the given subject (or subject/session)
  and insert them in the appropriate sidecar.
  """
  if (args.get('verbose')):
    sess = f" in session {session_id}" if session_id else ''
    print(f"Processing subject {subj_id}{sess}")
  fmri_image_paths = get_fmri_image_paths(args, layout, subj_id, session_id=session_id)
  if (fmri_image_paths):
    get_sidecar_and_insert(args, layout, fmri_image_paths, subj_id, session_id=session_id)


def validate_modality (modality):
  """
   Check the validity of the given modality string which must be one
   of the elements of the ALLOWED_MODALITIES list.
   Returns the canonicalized modality string or raises ValueError if
   given an invalid modality string.
  """
  if (modality in ALLOWED_MODALITIES):
    return modality
  raise ValueError(f"Modality argument must be one of: {ALLOWED_MODALITIES}")


def write_intended_for (args, intended_for_dict, pd_sidecar):
  "Convert intended_for dictionary to JSON and write it back to the sidecar file."
  permissions = get_permissions(pd_sidecar)   # get current file permissions
  os.chmod(pd_sidecar, 0o0640)                # make file writable
  output_JSON(intended_for_dict, file_path=pd_sidecar.path)
  os.chmod(pd_sidecar, permissions)           # restore original file permissions
