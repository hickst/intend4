# Intend4

This is a public code repository of the [Translational BioImaging Resource–MRI](https://research.arizona.edu/facilities/core-facilities/translational-bioimaging-resource-mri) core group at the [University of Arizona](https://www.arizona.edu/).

**Author**:  [Tom Hicks](https://github.com/hickst) and Dianne Patterson

**About**: This document describes the Intend4 tool. Intend4 provides a mechanism to ensure that the optimal fieldmaps, if present, will be used for susceptibility distortion correction of bold and DWI images respectively. Intend4 can generate or remove the `IntendedFor` field and its values from either the phasediff fieldmap JSON for bold data (e.g., *fmap/sub-188_phasediff.json*) or the reverse phase encode fieldmap JSON for DWI data (e.g., *fmap/sub-188_dir-PA_epi.json*).

This is important because DICOM-to-BIDS conversion tools do not always generate and populate the optional `IntendedFor` field; however, some BIDS apps, notably fMRIprep and QSIprep, rely on the presence of the `IntendedFor` field and its values to implement optimal susceptibility distortion correction. Without the populated `IntendedFor` field in the phasediff field map, fMRIprep will not use that image to correct the distortion in the fMRI images.  Likewise, without the populated `IntendedFor` field in the reverse phase encode field map, QSIprep will not use that image to correct the distortion in the DWI images.

For susceptibility distortion correction, **one and only one fieldmap** must be selected.  The intend4 tool will therefore skip subjects for whom the relevant fieldmap file is missing or fieldmap selection is ambiguous (e.g., multiple phasediff files exist for the bold images of a particular subject and session).

If there are **sessions**, Intend4 expects an `fmap` directory in each session subdirectory.

Intend4 will handle **permissions** on the JSON files it needs to alter, including read-only JSON files. The original permissions will be restored after the change.

## Using the Intend4 Tool

### **Prerequisite**: Docker or Apptainer

You must have Docker (or Apptainer) installed and working on your machine to use this project. For instructions on how to install Docker see [this link](https://docs.docker.com/get-docker/).

### **Step 1**: Download Intend4 Script and Test Data

- To run Intend4 using **Docker**, download the `intend4.sh` bash script file:

  `wget https://github.com/hickst/intend4/raw/main/intend4.sh`

  (If wget does not work for you, then put the address  https://raw.githubusercontent.com/hickst/intend4/main/intend4.sh into your browser and right-click to save a copy of the script )

  Ensure it is executable and in your path.

- To run Intend4 using **Apptainer**, download the `intend4_hpc.sh` bash script file:

   `wget https://github.com/hickst/intend4/raw/main/intend4_hpc.sh`

  (If wget does not work for you, then put the address  https://raw.githubusercontent.com/hickst/intend4/main/intend4_hpc.sh into your browser and right-click to save a copy of the script )

   Substitute `intend4_hpc.sh` for `intend4.sh` anywhere the documentation and examples refer to `intend4.sh`.

- To download the test dataset `BIDS_MRI.zip`:
  - Select this link for [the BIDS_MRI.zip file](https://bitbucket.org/dpat/neuro4rii/src/main/data/BIDS_MRI.zip):
  - Choose `Open raw` under the `...` on the right and the file should download.

  The `BIDS_MRI.zip` file includes 5 subjects, using the BIDS file structure, all with *dwi*, *fmap*, and *func* directories, but the image files are empty so the dataset is tiny (~100 Kb).

- Alternatively, you can use `wget` to retrieve the zip file:

  `wget https://bitbucket.org/dpat/neuro4rii/raw/main/data/BIDS_MRI.zip`

- Unzip the `BIDS_MRI.zip` file and navigate to the `BIDS_MRI/data` directory.

### **Step 2**: Learn to Run the **Intend4** container on Test Data

- The script assumes you are running from your **BIDS data directory**!
  This is the directory where your NIfTI BIDS data and the `dataset_description.json` reside.

```
BIDS_MRI
├── data
│   ├── sub-188
│   ├── sub-190
│   ├── sub-194
│   ├── sub-215
│   └── sub-221
```

- If you have not yet pulled the `hickst/intend4` Docker container, the Docker script will do that the first time you run it.
- If you use `--participant-label`, subject numbers are specified by the number only!
  - For example, `sub-078` would be specified as `078`.

- By default, the `intend4.sh` script runs in **verbose** mode to provide maximal information.

- Intend4 will handle permissions on the JSON files it needs to alter. Even if the files are read-only, changes will be made, and then the original permissions will be restored after the changes.
- Intend4 will handle valid BIDS directories, including sessions.

**Example 1**: Modify the phasediff fieldmap JSON file for one subject, sub-188:

`intend4.sh bold --participant-label 188`

If you are running Docker and have not pulled the Docker container, the Docker script will do that now:

```
Unable to find image 'hickst/intend4:latest' locally
latest: Pulling from hickst/intend4
bb7d5a84853b: Pull complete
f02b617c6a8c: Pull complete
d32e17419b7e: Pull complete
c9d2d81226a4: Pull complete
3c24ae8b6604: Pull complete
8a4322d1621d: Pull complete
0bde298e076a: Pull complete
e169b6c7c628: Pull complete
1b7366f8a3aa: Pull complete
6a5053af2d01: Pull complete
4f4fb700ef54: Pull complete
625f71f679c0: Pull complete
b1fcf0200c79: Pull complete
b4fed0aeb8b9: Pull complete
1a889060d520: Pull complete
ed2a74acbd84: Pull complete
ccb71067e190: Pull complete
04802e957995: Pull complete
415c42501533: Pull complete
Digest: sha256:5a9b06a6581ebe5ff96304d64a9dd282c9815261c1a59a5005b84429ce12e478
Status: Downloaded newer image for hickst/intend4:latest
(intend4): Modifying IntendedFor field in sidecar files for modality 'bold'.
(intend4): Processing subject 188
(intend4): Modified IntendedFor fields in 1 phasediff sidecars.
```

 Examine the phasediff.json file to confirm that it has been altered:

```bash
cat sub-188/fmap/sub-188_phasediff.json
```

You should see the `IntendedFor` field:

```json
"IntendedFor": [
    "func/sub-188_task-nad1_run-01_bold.nii.gz",
    "func/sub-188_task-nad1_run-02_bold.nii.gz",
    "func/sub-188_task-nad1_run-03_bold.nii.gz",
    "func/sub-188_task-nad1_run-04_bold.nii.gz"
  ],
```

**Example 2**: Remove the values from the `IntendedFor` field and reinspect the JSON file again.

```bash
intend4.sh bold --participant-label 188 --remove
```

You see the verbose message:

```
(intend4): Removing IntendedFor field in sidecar files for modality 'bold'.
(intend4): Processing subject 188
(intend4): Removed IntendedFor fields in 1 phasediff sidecars.
```

Inspect the file:

```bash
cat sub-188/fmap/sub-188_phasediff.json
```

The values for `IntendedFor` have been removed:

```json
 "IntendedFor": [],
```

**Example 3**: Modify the Reverse Phase encoded image JSON file (`fmap/*.epi`) for all subjects:

```bash
intend4.sh dwi
```

You see the verbose message:

```
(intend4): Modifying IntendedFor field in sidecar files for modality 'dwi'.
(intend4): Processing subject 215
(intend4): Processing subject 188
(intend4): Processing subject 194
(intend4): Processing subject 190
(intend4): Processing subject 221
(intend4): Modified IntendedFor fields in 5 epi sidecars.
```

Inspect the reverse-phase-encode file:

```bash
cat sub-188/fmap/*epi.json
```

You should see the `IntendedFor` field:

```json
"IntendedFor": [
    "dwi/sub-188_acq-AP_dwi.nii.gz"
  ],
```

  **Example 4**: Add the phasediff `IntendedFor` values for all subjects:

```bash
intend4.sh bold
```

You see the verbose message:

```
(intend4): Modifying IntendedFor field in sidecar files for modality 'bold'.
(intend4): Processing subject 215
(intend4): Processing subject 221
Error: phasediff sidecar file is missing for subject 221. Skipping...
(intend4): Processing subject 194
(intend4): Processing subject 188
(intend4): Processing subject 190
(intend4): Modified IntendedFor fields in 5 phasediff sidecars.
```

_**Note**: Intend4 alerts you to the missing phasediff image for sub-221!_

### Getting Usage Help

To see a help (usage) message for `intend4.sh` (or `intend4_hpc.sh`), call the tool with the special ***help flag*** (`-h` or `--help`):
```bash
$ intend4.sh -h

This script calls the 'intend4' docker container.
Run it from the bids data directory containing your subjects.
Modality is the only required argument: specify 'bold' or 'dwi'.

Examples:
  Modify the phasediff fieldmap JSON files for all subjects:
    > /home/dkp/bin/intend4.sh bold

  Modify the Reverse Phase encoded image JSON file (fmap/*.epi) for all subjects:
    > /home/dkp/bin/intend4.sh dwi

  To remove the phasediff IntendedFor values, add the flag --remove after the modality:
    > /home/dkp/bin/intend4.sh bold --remove

  Modify the phasediff fieldmap JSON files for just subjects 078 and 215:
    > /home/dkp/bin/intend4.sh bold --participant-label 078 215

Usage: /home/dkp/bin/intend4.sh -h | --help
       OR
       /home/dkp/bin/intend4.sh {bold, dwi} [--participant-label [SUBJ_IDS ...]] [--remove]
```


## License

This software is licensed under Apache License Version 2.0.

Copyright (c) The University of Arizona, 2021. All rights reserved.
