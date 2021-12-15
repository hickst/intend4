# Intend4

This is a public code repository of the [Translational BioImaging Resource–MRI](https://research.arizona.edu/facilities/core-facilities/translational-bioimaging-resource-mri) core group at the [University of Arizona](https://www.arizona.edu/).

**Author**:  [Tom Hicks](https://github.com/hickst) and Dianne Patterson

**About**: This document describes the intend4 tool. Intend4 provides a mechanism to ensure that the optimal fieldmaps, if present, will be used for susceptibility distortion correction of bold and dwi images respectively. intend4 can generate or remove the `IntendedFor` field and its values from either the phasediff fieldmap json for bold data (e.g., *fmap/sub-188_phasediff.json*) or the reverse phase encode fieldmap json for dwi data (e.g., *fmap/sub-188_dir-PA_epi.json*).  This is important because DICOM-to-BIDS conversion tools do not always generate and populate the optional IntendedFor field; however, some BIDS apps, notably fMRIprep and QSIprep, rely on the presence of the IntendedFor field and its values to implement optimal susceptibility distortion correction. Without the populated IntendedFor field in the phasediff field map, fMRIprep will not use that image to correct the distortion in your fmri images.  Likewise, without the populated IntendedFor field in the reverse phase encode field map, QSIprep will not use that image to correct the distortion in your dwi images. 

For susceptibility distortion correction, one and only one fieldmap must be selected.  The intend4 tool will therefore skip subjects for whom the relevant fieldmap file is missing or fieldmap selection is ambiguous (e.g., multiple phasediff files for the bold images of a particular subject and session).

## Using the Intend4 Tool

### **Prerequisite**: Docker

You must have Docker installed and working on your machine to use this project. For instructions on how to install Docker see [this link](https://docs.docker.com/get-docker/).

### **Step 1**: Download Intend4 Test Data

- Download the dataset: [BIDS_DATA.zip](https://bitbucket.org/dpat/neuro4rii/src/main/data/BIDS_MRI.zip).  It includes 5 subjects, using the BIDS file structure, all with *dwi*, *fmap* and *func* directories, but the image files are empty so the dataset is tiny (~100 Kb).  

- Unzip the file and navigate to the BIDS_MRI/data directory.

### **Step 2**: Learn to Run the **Intend4** Docker container on Test Data

**Example 1**: From the /data directory, run intend4 to generate and populate the *IntendedFor* field to the fmap phasediff.json files for all participants.  

***Note** The container-internal bindmount is `/intend4` internally (not `/data`)!*

```bash
  > docker run -it --rm -v ${PWD}:/intend4 hickst/intend4:latest bold --verbose
```

***Note**: It is highly recommended to use the **verbose mode flag** (`-v` or `--verbose`) to produce informational messages while processing, unless you have a specific reason not to do so.*

The verbose flag will list the status of each processed subject:

```bold
(intend4): Modifying IntendedFor field in sidecar files for modality 'bold'.
(intend4): Processing subject 194
(intend4): Processing subject 190
(intend4): Processing subject 215
(intend4): Processing subject 221
Error: phasediff sidecar file is missing for subject 221. Skipping...
(intend4): Processing subject 188
(intend4): Modified IntendedFor fields in 5 phasediff sidecars.
```

For all subjects, the IntendedFor field is created in the fmap/\*phasediff.json file, e.g.,

```bash
 "IntendedFor": [
    "func/sub-188_task-nad1_run-01_bold.nii.gz",
    "func/sub-188_task-nad1_run-02_bold.nii.gz",
    "func/sub-188_task-nad1_run-03_bold.nii.gz",
    "func/sub-188_task-nad1_run-04_bold.nii.gz"
  ],
```

Display the phasediff json files for each subject and locate the created field.

**Example 2**: Run intend4 to remove the *IntendedFor* field values from the fmap/\*phasediff.json file:

```bash
  > docker run -it --rm -v ${PWD}:/intend4 hickst/intend4:latest bold --remove
```
For all subjects, the IntendedFor field values are removed from the phasediff fieldmap sidecars, e.g.,
```bash
 "IntendedFor": [],
```

**Example 3**: Navigate to the parent directory, *BIDS_MRI*. In this example, docker bind mounts *BIDS_MRI* instead of the subdirectory *data*. It is therefore necessary to provide an additional argument specifying the location of the bids_dir: `--bids-dir=data`. This time, run intend4 with the `dwi` modality to add the *IntendedFor* field to the json file for the Reverse-Phase-Encode image (fmap/\*epi.json). 

```bash
  > docker run -it --rm -v ${PWD}:/intend4 hickst/intend4:latest dwi --bids-dir data --verbose
```

The verbose flag will again generate an informational message:

```bash
(intend4): Modifying IntendedFor field in sidecar files for modality 'dwi'.
(intend4): Processing subject 194
(intend4): Processing subject 215
(intend4): Processing subject 190
(intend4): Processing subject 221
(intend4): Processing subject 188
(intend4): Modified IntendedFor fields in 5 epi sidecars.
```

For all subjects, the *IntendedFor* field is created and populated in the fmap/\*epi.json file, e.g.,

```bash
"IntendedFor": [
    "dwi/sub-188_acq-AP_dwi.nii.gz"
  ],
```

### Getting Usage Help

To see a help (usage) message for a intend4, call the tool with the special ***help flag*** (`-h` or `--help`):
```bash
  > docker run -it --rm -v ${PWD}:/intend4 hickst/intend4:latest --help
usage: intend4 [-h] [-v] [--bids-dir BIDS_DIR] [--participant-label [SUBJ_IDS ...]] [--remove] {bold,dwi}

intend4: Adds or removes 'IntendedFor' info to the JSON sidecars, for one or more subjects.

positional arguments:
  {bold,dwi}            Modality of the image files. Must be one of: ['bold', 'dwi']

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Print informational messages during processing [default: False (non-verbose mode)].
  --bids-dir BIDS_DIR, --bids_dir BIDS_DIR
                        (Optional) Path to BIDS data directory [default: current directory]
  --participant-label [SUBJ_IDS ...], --participant_label [SUBJ_IDS ...]
                        (Optional) Space-separated subject number(s) to process [default: process all subjects]
  --remove              REMOVE IntendedFor entries for the selected modality [default: False].
```



## License

This software is licensed under Apache License Version 2.0.

Copyright (c) The University of Arizona, 2021. All rights reserved.

