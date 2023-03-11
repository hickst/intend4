#!/bin/bash
#
# Shell script to run the intend4 program from the intend4 Apptainer container.
#	This script will add and populate the IntendedFor field in the appropriate JSON fieldmap files.
# This script mounts the required directories and calls the intend4 program inside the container.
# The script will ultimately live here: https://bitbucket.org/dpat/neuro4rii/src/main/bash_scripts/

# echo "ARGS=$*"

PROG=$0
export SIF=${SIF:-/contrib/singularity/shared/neuroimaging}

help () {
	echo ""
	echo "This script calls the 'intend4' apptainer container."
	echo "Run it in an interactive session and from the bids data directory containing your subjects."
	echo "Modality is the only required argument: specify 'bold' or 'dwi'."
	echo ""
	echo "Examples:"
  echo "  Modify the phasediff fieldmap JSON files for all subjects:"
	echo "    > $PROG bold"
  echo ""
  echo "  Modify the Reverse Phase encoded image JSON file (fmap/*.epi) for all subjects:"
	echo "    > $PROG dwi"
  echo ""
  echo "  To remove the phasediff IntendedFor values, add the flag --remove after the modality:"
	echo "    > $PROG bold --remove"
  echo ""
  echo "  Modify the phasediff fieldmap JSON files for just subjects 078 and 215:"
	echo "    > $PROG bold --participant-label 078 215"
  echo ""
}

usage () {
  echo ""
  echo "Usage: $PROG -h | --help"
  echo "       OR"
  echo "       $PROG {bold, dwi} [--participant-label [SUBJ_IDS ...]] [--remove]"
}

if [ $# -lt 1 ]; then
  usage
  exit 1
fi

if [ "$1" = '-h' -o "$1" = '--help' ]; then
  help
  usage
  exit 2
fi

MODALITY=$1
shift
if [ "$MODALITY" != 'bold' -a "$MODALITY" != 'dwi' ]; then
  echo ""
  echo "ERROR: Unrecognized modality: must be one of 'bold' or 'dwi'."
  usage
  exit 3
fi

# echo "ARGS=$@"
# docker run -it --rm --name intend4 -v "${PWD}":/data ${IMG} "${MODALITY}" --verbose $@
apptainer run --bind "${PWD}":/data ${SIF}/intend4.sif   "${MODALITY}" --verbose $@