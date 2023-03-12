# Program to insert IntendedFor array in phasediff JSON sidecar files in order
# to trigger fMRIPrep or QSIPrep to run SDC (Susceptibility Distortion Correction).
#   Written by: Tom Hicks and Dianne Patterson. 4/21/21.
#   Last Modified: Remove deprecated setting.
#
import os
import sys
import bids
import json
from bids import BIDSLayout

from intend4 import ALLOWED_MODALITIES, BIDS_DIR
from intend4.file_utils import get_permissions


IMAGE_EXT = ['nii.gz', 'nii']
PHASEDIFF_SUFFIX = 'phasediff'
RPE_SUFFIX = 'epi'
SIDECAR_EXT = 'json'
SUBJ_DIR_PREFIX = 'sub-'


def do_subjects(modality, args):
  """
  For the specified subject (or all subjects), find and modify the fieldmap sidecars
  which will be used to correct images with the given modality.
  """
  # use the optionally specified BIDS data dir or default to current directory
  bids_dir = args.get('bids_dir', BIDS_DIR)

  # analyze BIDS data directory but exit if not valid to avoid changing any files
  sys.tracebacklimit = 0
  try:
    layout = BIDSLayout(bids_dir, validate=True)
  except:
    raise RuntimeError(
      f"BIDS validator got an error while processing the BIDS Data directory.")

  # use the optionally specified list of subjects or default to all subjects
  subj_ids = args.get('subj_ids')
  if (subj_ids is not None):
    selected_subjects = subj_ids
  else:
    selected_subjects = layout.get_subjects()

  mod_count = 0
  for subj_id in selected_subjects:
    mod_count += do_single_subject(modality, args, layout, subj_id)
  return mod_count


def do_single_subject(modality, args, layout, subj_id):
  """
  For a single subject (and optional sessions), find and modify the fieldmap sidecar
  which will be used to correct the image with the given modality.
  """
  mod_count = 0
  sessions = sessions_for_subject(layout, subj_id)
  if (sessions):             # if there are sessions in use
    for sess_num in sessions:
      update_fieldmap(modality, args, layout, subj_id, session_id=sess_num)
      mod_count += 1
  else:                      # else sessions are not being used
    update_fieldmap(modality, args, layout, subj_id)
    mod_count += 1
  return mod_count


def get_fieldmap_suffix (modality, args=None):
  """
  Compute the fieldmap suffix for correcting images of the given modality, allowing
  for special cases specified by additional arguments (in the future).
  """
  return PHASEDIFF_SUFFIX if (modality == 'bold') else RPE_SUFFIX


def get_image_paths (modality, args, layout, subj_id, session_id=None):
  """
  Return a list of modality-specific image paths for the given subject (or subject/session).
  Assumes that the modality argument is the same string used for the BIDS file suffix
  for that modality.
  """
  bids_file_objects = layout.get(subject=subj_id, session=session_id,
                                 extension=IMAGE_EXT, suffix=modality)
  return [subjrelpath(bids_file_object.relpath) for bids_file_object in bids_file_objects]


def get_sidecar_and_modify (modality, args, layout, image_paths, subj_id, session_id=None):
  """
  Insert the given image paths into the appropriate sidecar data structure for
  for identified subject (or subject/session). Then rewrite the (modified) sidecar.
  Raise an error if more than one sidecar is found per subject (or subject/session).
  """
  fieldmap_suffix = get_fieldmap_suffix(modality, args)
  sidecars = layout.get(target='subject', subject=subj_id, session=session_id,
                        suffix=fieldmap_suffix, extension=SIDECAR_EXT)
  num_sidecars = len(sidecars)
  if (num_sidecars < 1):
    sess = f" in session {session_id}" if session_id else ''
    err_msg = f"Error: {fieldmap_suffix} sidecar file is missing for subject {subj_id}{sess}. Skipping..."
    print(err_msg, file=sys.stderr)
    return
  elif (num_sidecars > 1):
    sess = f" in session {session_id}" if session_id else ''
    err_msg = f"Error: Found more than 1 {fieldmap_suffix} sidecars for subject {subj_id}{sess}. Skipping..."
    print(err_msg, file=sys.stderr)
    return
  else:
    sidecar = sidecars[0]
    modified_contents = modify_intended_for(image_paths, sidecar.get_dict(), remove=args.get('remove'))
    rewrite_sidecar(modified_contents, sidecar.path)


def has_session(layout, subj_id):
  "Tell whether the identified subject has sessions or not."
  return subj_id in layout.get(return_type='id', target='subject', session=layout.get_sessions())


def modify_intended_for (image_paths, contents, remove=False):
  """
  Modify the given contents dictionary, storing the given image paths under the
  IntendedFor key. If IntendedFor key already exists, its value is replaced by the
  given image paths. If remove flag is True, then the value is replaced by an empty list.
  Returns the sidecar contents dictionary, sorted by keywords.
  """
  contents['IntendedFor'] = [] if remove else image_paths
  sorted_dict = dict(sorted(contents.items()))
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


def rewrite_sidecar (modified_contents, sidecar):
  "Convert the contents dictionary to JSON and write it back to the sidecar file."
  permissions = get_permissions(sidecar)   # get current file permissions
  os.chmod(sidecar, 0o0640)                # make file writable
  output_JSON(modified_contents, file_path=sidecar)
  os.chmod(sidecar, permissions)           # restore original file permissions


def sessions_for_subject(layout, subj_id):
  "Return a list of session IDs for the identified subject."
  return layout.get(return_type='id', target='session', subject=subj_id)


def subjrelpath (subjpath):
  """
  Return the subject-relative path for the given filepath string or None if the
  given filepath is not relative to any subject.
  """
  if (subjpath.startswith(SUBJ_DIR_PREFIX)):
    ndx = subjpath.find('/')
    if (ndx != -1):
      return subjpath[ndx+1:]
    else:
      raise TypeError(f"Error: Unable to remove subject prefix from {subjpath}: no '/' found.")
  else:                                # given file is not relative to a subject directory
    return None


def update_fieldmap(modality, args, layout, subj_id, session_id=None):
  """
  Get paths to all images for the given subject (or subject/session) with the given modality,
  and insert them in the appropriate sidecar.
  """
  if (args.get('verbose')):
    prog_name = args.get('PROG_NAME')
    prog_prefix = f"({prog_name}): " if prog_name else ''
    sess = f" in session {session_id}" if session_id else ''
    print(f"{prog_prefix}Processing subject {subj_id}{sess}")
  image_paths = get_image_paths(modality, args, layout, subj_id, session_id=session_id)
  if (image_paths):
    get_sidecar_and_modify(modality, args, layout, image_paths, subj_id, session_id=session_id)


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
