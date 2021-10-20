# Readme IntendedFor
**Date** May 4, 2021   
**Author** Dianne Patterson, Ph.D.  

## Background and Problem

My hope is that this information is dated and this tool will be unecessary in the future.
fMRIPrep does not default to using your fieldmaps to do susceptibility distortion correction (SDC). Instead, the phasediff fieldmap sidecar (e.g. fmap/sub-188_phasediff.json) must include an IntendedFor list; and the IntendedFor list must contain the relative path to the bold fMRI images. The relative path should include only the path from within the subject directory.

Here is an example of the IntendedFor list in fmap/sub-188_phasediff.json. This is an example for a subject without sessions, and it indicates that SDC should be used for all four of these fMRI runs:

```json
 "IntendedFor": [
    "func/sub-188_task-nad1_run-01_bold.nii.gz",
    "func/sub-188_task-nad1_run-02_bold.nii.gz",
    "func/sub-188_task-nad1_run-03_bold.nii.gz",
    "func/sub-188_task-nad1_run-04_bold.nii.gz"
  ],
```

Here is an example for a subject with sessions (and only two bold images):

```json
 "IntendedFor": [
    "ses-ctbs/func/sub-219_ses-ctbs_task-rest_run-01_bold.nii.gz",
    "ses-ctbs/func/sub-219_ses-ctbs_task-rest_run-02_bold.nii.gz"
  ],
``` 
To determine whether SDC was used by fMRIPrep, view the subject HTML report.

### Current solutions
- Adding the Intendedfor at the time you convert from Dicom.  Some conversion tools will do this.  Heudiconv will allow you to create [custom code](https://fw-heudiconv.readthedocs.io/en/latest/heuristic.html#fw_heudiconv.example_heuristics.demo.IntendedFor) and include the IntendedFor.  These choices work well if you have a homogeneous dataset and you realize this is an issue before you do the Dicom to NIfTI conversion.
- Add the field manually after the fact (being very careful not to violate the JSON standards).  You can validate JSON with the [JSON Linter](https://jsonlint.com/).
- Use this **diannepat/intend4 dockerized Python tool** to find all BOLD fMRI files for a particular subject and insert the IntendedFor into an existing phasediff JSON file in a bids directory. This is useful if the dicom-to-bids conversion solution did not create the Intendedfor field in the phasediff fieldmap sidecar.
    - **WARNING** 
        - This solution will overwrite any existing IntendedFor field.
        - This solution will add all and only the BOLD images to the IntendedFor field.
        - This solution will fail if it encounters multiple phasediff images. There should only be one.

## Installation

- Download the Docker container (this requires that Docker is installed)
`docker pull diannepat/intend4`  
- Download the **intend4_wrap.sh** bash script to facilitate running:
[intend4_wrap.sh](https://bitbucket.org/dpat/tools/raw/master/LIBRARY/intend4_wrap.sh)

## Usage 

- The **intend4_wrap.sh** script assumes you are running from your bids directory.  
- Run the script with no arguments display a help message. 
- You may also run the docker command interactively: 

Run all subjects in the current directory
```bash
docker run -it --rm --name intend4 -v ${PWD}:/data diannepat/intend4:latest --verbose --bids_dir=/data
```
Or run individual subjects (e.g., sub-078 and sub-188):
```bash
docker run -it --rm --name intend4 -v ${PWD}:/data diannepat/intend4:latest --verbose --bids_dir=/data --participant_label 078 188
```