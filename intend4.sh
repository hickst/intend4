#!/bin/bash
#
# Shell script to run the intend4 program from the intend4 Docker container.
#    This script will add and populate the IntendedFor field in the appropriate JSON fieldmap files.
#    This script mounts the required directory and calls the Intend4 program inside the container.
#
# echo "ARGS=$*"

PROG=$(basename $0)
IMG=hickst/intend4

help () {
  echo "Usage: $PROG [-h] {bold,dwi} [--participant-label [SUBJ_IDS ...]] [--remove]"
  echo ''
  echo 'intend4: Adds or removes "IntendedFor" info to the JSON sidecars, for one or more subjects.'
  echo ''
  echo 'required argument:'
  echo '  {bold,dwi}        Modality of the image files. Must be one of: ["bold", "dwi"]'
  echo ''
  echo 'optional arguments:'
  echo '  -h, --help        Show this help message and exit'
  echo '  --participant-label [SUBJ_IDS ...], --participant_label [SUBJ_IDS ...]'
  echo '                    (Optional) Space-separated subject number(s) to process'
  echo '  --remove          REMOVE IntendedFor entries for the selected modality [default: False].'
  echo ''
  echo ''
  echo 'Examples:'
  echo '  Modify the phasediff fieldmap JSON files for all subjects:'
  echo "    > $PROG bold"
  echo ''
  echo '  Modify the Reverse Phase encoded image JSON file (fmap/*.epi) for all subjects:'
  echo "    > $PROG dwi"
  echo ''
  echo '  To REMOVE the phasediff IntendedFor values add the flag --remove:'
  echo "    > $PROG bold --remove"
  echo ''
  echo '  Modify the phasediff fieldmap JSON files for just subjects 078 and 215:'
  echo "    > $PROG bold --participant-label 078 215"
}

if [ $# -lt 1  -o "$1" = "-h" -o "$1" = "--help" ]
then
  help
  exit 1
fi

# echo "ARGS=$@"

MODALITY=$1
shift
if [ "$MODALITY" != 'bold' -a "$MODALITY" != 'dwi' ]; then
  echo "$PROG: ERROR: First argument must be a valid modality: one of 'bold' or 'dwi'."
  echo ""
  help
  exit 2
fi

docker run -it --rm --name intend4 -u $UID -v "${PWD}":/data ${IMG} --verbose -m ${MODALITY} $@
