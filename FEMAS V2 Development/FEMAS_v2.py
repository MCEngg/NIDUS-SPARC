# FEMAS_v2.py
# Fetal Echo Mask Automation Script Version 2.0
# 
# Last Modified: Jun 13, 2025 - 3:33 PM
# Last Modified By: Matthew Chin
# Status: Deployed
#
# Script Summary:
# Using the hierarchy JSON path loop through all of the Study Instance UID's and look at each specific DICOM
# folder for the JPG frames. Then use the FEMAS_v1.3 masking and overlay function to create the masks and overlays.
# Before saving the masks and overlays, create a directory for each masks and overlays and store them in the respective
# directories.
# 
# The script will create a Overlay directory and a Mask directory in each of the DICOM folders and will store the respective images
# in each folder.
# 
# Important Comments:
# This file should be kept in the same directory as the annotation and Fetal-Echo hierarchy JSON files. It should also be 
# located next to the JPGMO folder for the selected study.
# 
# Worst Case Scenario: O(n^2)
# 
# DISCLAIMER!
# Portions of this script is material provided by ChatGPT. This script is optimized accordingg to advice given by ChatGPT.
# 

# System & File Imports
import os
import json

# Masking & Overlay Imports
import numpy as np
import cv2

# OPERATIONAL & TESTED
def masks_and_overlays(vertices, height, width, image, mask_path, overlay_path, jpg_name):
    # AI Generated Code
    # Create the array of zeros using the height and width of the image (in pixels).
    mask = np.zeros((height, width), dtype = np.uint8)

    # Fill in a polygon using the vertices found before and colour them white.
    cv2.fillPoly(mask, [vertices], 255)

    # Overlay the mask onto a copy of the image.
    overlay = image.copy()
    overlay[mask == 255] = [0, 0, 255]
    overlaid_image = cv2.addWeighted(overlay, 0.5, image, 0.5, 0)

    # Save the Mask & Overlay Using ABS Paths
    cv2.imwrite(os.path.join(mask_path, jpg_name), mask)
    cv2.imwrite(os.path.join(overlay_path, jpg_name), overlaid_image)
    return 2


# OPERATIONAL & TESTED
def main():

    print("------ SCRIPT EXECUTE --- FEMAS V2 ---------")

    # Initialize Folder and File Paths
    main_folder_path = os.path.dirname(os.path.abspath(__file__))
    annotation_path = os.path.join(main_folder_path, "Fetal-Echo-05_[ANNOTATOR-DATA][ANNOTATE-SCHEMA].json")
    hierarchy_path = os.path.join(main_folder_path, "Fetal_Echo_05.json")

    # Open and Load the JSON files for use.
    with open(hierarchy_path) as hierarchy_File:
        hierarchy_json = json.load(hierarchy_File)

    with open(annotation_path) as annotation_File:
        annotation_json = json.load(annotation_File)

    # Intialize the directory path for the JPG images.
    jpg_mask_overlay_directory = os.path.join(main_folder_path, "Fetal-Echo-05_JPGMO")

    # Initialize Total Counter
    all_masks_AND_overlays = 0

    # For every Study Instance UID contained in the JSON file.
    for study in hierarchy_json:
        
        # Create the path that leads to the Study ID (contains the DICOMS)
        poten_path = os.path.join(jpg_mask_overlay_directory,study)
        
        # Check to see if the ID path exists.
        if os.path.exists(poten_path):

            # If it does, load all the DICOM names into the list.
            dicom_set = set(hierarchy_json[study])

            # Go through the whole annotations looking for the specific DICOM ID
            for entry in annotation_json['annotations']:
                
                # Varaible to determine what kind of mask and overlay is necessary.
                mask_type = entry['annotation']['type']

                # If an entry in the annotations file matches with a DICOM ID
                if (entry['imageId'] in dicom_set) and (mask_type == "box" or mask_type == "polygon"):
                    
                    # JPG Extension
                    jpg_exten = f"{entry['frame']:04d}.jpg"

                    # Create the path for the JPG's that have annotations.
                    jpgImage_path = os.path.join(poten_path, entry['imageId'], jpg_exten)
                    image = cv2.imread(jpgImage_path)

                    # If the path doesn't exist.
                    if image is None:
                        
                        # Raise an error if we cant find the DICOM frame and list details. 
                        raise FileNotFoundError(f"DICOM Frame Not Found!\nDICOM:{entry['imageId']}    FRAME: {entry['frame']}")
                    
                    # Grab image details for masks and overlays.
                    height, width = image.shape[:2]

                    # Create the Save Directories for the masks and overlays.
                    mask_path = os.path.join(poten_path, entry['imageId'], "Masks")
                    overlay_path = os.path.join(poten_path, entry['imageId'], "Overlays")
                    os.makedirs(mask_path, exist_ok = True)
                    os.makedirs(overlay_path, exist_ok = True)

                    # Create Polygon Mask & Overlay.
                    if mask_type == 'polygon':
                        
                        # Create an array of vertices and reshape the data that is stored in the JSON.
                        vertices_array = np.array(entry['annotation']['data'], dtype = np.int32).reshape((-1,1,2))

                    # Create Box Mask & Overlay.
                    elif mask_type == 'box':
                        
                        # Top Left Hand Corner (TLHC)
                        x_LeftTop = int(entry['annotation']['data'][0])
                        y_LeftTop = int(entry['annotation']['data'][1])
                        
                        # Bottom Right Hand Corner (BRHC)
                        x_RightBottom = int(entry['annotation']['data'][2])
                        y_RightBottom = int(entry['annotation']['data'][3])
                        
                        # AI Generated Code:
                        vertices_array = np.array([[x_LeftTop,y_LeftTop],[x_RightBottom,y_LeftTop],[x_RightBottom,y_RightBottom],[x_LeftTop,y_RightBottom]]).reshape((-1,1,2))

                    # Create And Save Masks & Overlays (Increment Counter Too)
                    all_masks_AND_overlays += masks_and_overlays(vertices_array, height, width, image, mask_path, overlay_path, jpg_exten)
    
        # Print a warning that there is no Study folder and provide details.
        else:
            print("Warning! There is no study folder for study: " + study)

    print("Masks & Overlays Added.")
    print(f"Masks Added: {all_masks_AND_overlays/2}")
    print(f"Overlays Added: {all_masks_AND_overlays/2}")
    print(f"Total Number of Masks & Overlays Added: {all_masks_AND_overlays}")
    print("------ SCRIPT EXIT ------ FEMAS V2 ---------")

if __name__ == "__main__":
    main()