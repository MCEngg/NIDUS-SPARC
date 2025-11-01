#json_UID_detector.py

# Last Modified: Jun 04, 2025 - 1:52 PM
# Last Modified By: Matthew Chin

# Test Program Objectives:
# Using data in the hardcoded json file, use the indicated StudyUID to determine the existance of the folder.
# If the folder exists, load the imageId's and place them into an array.

import json
import os

hardcode_json = "C:/Users/thech/OneDrive/Desktop/NIDUS/Fetal Echo Project/Image Segmentation Mask Program/Fetal_Echo_05.json"
hardcode_mainFold = "C:/Users/thech/OneDrive/Desktop/NIDUS/Fetal Echo Project/Image Segmentation Mask Program/"

json_file = open(hardcode_json)
json_data = json.load(json_file)

# DICOM List
dicom_list = []


# For every studyUID object in the JSON file.
for studyUID in json_data:
    # Create the potential UID path that the images will be stored in.
    potentialUID_Path = hardcode_mainFold + studyUID

    # Check to see if that folder exists at the absolute path.
    if os.path.exists(potentialUID_Path):
        print("StudyUID: " + studyUID)
        # Print out all of the dicoms listed under the existing folder.
        for dicom in json_data[studyUID]:
            print("imageId: " + dicom)
            # Add the dicom names to the dicom list.
            dicom_list.append(dicom)
    
    # Print a warning otherwise that there is no UID folder for the specific UID.
    else:
        print("Warning: There is no image folder for studyUID: " + studyUID)

    print()
        
json_file.close()

# Operational, program successfully added the dicom imageId's to the list.
print("Contained in dicomList")
for dicom in dicom_list:
    print("imageId: " + dicom)