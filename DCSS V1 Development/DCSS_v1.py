# DCSS_v1.py
# DICOM Conversion Storage Script Version 1.0
# 
# Last Modified: 06/16/2025 - 10:57 AM
# Last Modified: Matthew Chin
# Status: Deployed -- Changes Pending
# 
# Script Summary:
# Using the Fetal Echo Batch Hash Excel file and the DCM files and the DICOM ID's create directories
# for each DICOM ID. Then the script should then enter into such directory and store JPG frames of the converted
# DCM file. Note that the DICOM ID folders should be stored in their own directory that is labelled after the
# Study Instance UID found in the DCM attributes.
#
# The script will create a Study Instance UID for groups of DICOM ID's. DICOM ID folders will be stored in the Study Instance UID
# folder and will contain JPG frames converted from the DCM files.
# 
# Important Comments:
# This file should be kept in the same directory as the annotation JSON file and the Fetal Echo JSON file.
# This file should not be kept in the same directory as the DCM files. The program will reach into that directory to access them and create a couple
# of nested directories. 
#
# Worst Case Scenario: O(n^4) - Does not implement parallel processing.
# 
# BEWARE OF HARDCODED PATHS. These will need to change if they are not already
# THIS SCRIPT IS NOT COMPLETELY EFFICIENT. This script does not take advantage of parallel processing.
# With a data set of ~100 DCM files, each producing around 200-500 JPG frames, the process took ~30 min to complete.
#
# DISCLAIMER!
# Portions of this script is material provided by ChatGPT. This script is optimized according to advice provided by ChatGPT.
# 

# System & File Imports
import os
import json

# DICOM Conversion Imports 
import numpy as np
import pydicom
from PIL import Image

# Excel File Imports
import pandas as pd


# OPERATIONAL & TESTED
def normalize_pixel_array(arr):
    # We need to normailze the array to 8 bits instead of the standard 16 bits for DICOM files.
    arr = arr.astype(np.float32)
    arr -= np.min(arr)
    arr /= np.max(arr)
    arr *= 255.0
    return arr.astype(np.uint8)

# OPERATIONAL & TESTED
def dicom_to_jpg_frames(dicom_path, jpg_mask_overlay_directory, dicom_id):
    # Load the DICOM file.
    dcm = pydicom.dcmread(dicom_path)

    # Output folder path.
    output_folder = os.path.join(jpg_mask_overlay_directory, dcm.StudyInstanceUID, dicom_id)

    # Check if it’s a multi-frame image or single image.
    if hasattr(dcm, 'PixelData'):
        # Create output folder if it doesn't exist.
        os.makedirs(output_folder, exist_ok=True)

        # Extract pixel data and convert to numpy array.
        # If the DCM file has the attribute 'NumberOfFrames' then it must be a multiframe image.
        if hasattr(dcm, 'NumberOfFrames'):
            # Assign a frames variable to the pixel array of the multiple images in the DCM.
            frames = dcm.pixel_array
            # For every number and frame in the frames array:
            for i, frame in enumerate(frames):
                # Normalize the frame (For conversion to JPG).
                frame_normalized = normalize_pixel_array(frame)
                # Turn the array back into an image.
                img = Image.fromarray(frame_normalized)
                # Save the image.
                img.save(os.path.join(output_folder, f"{i:04d}.jpg"))
        else:
            # Single-frame DICOM.
            frame = dcm.pixel_array
            frame_normalized = normalize_pixel_array(frame)
            img = Image.fromarray(frame_normalized)
            img.save(os.path.join(output_folder, "0000.jpg"))
        print(f"Converted {dicom_id} to JPGs.")
    else:
        print("No pixel data found in the DICOM file.")
    
    return (1,dcm.NumberOfFrames)

# OPERATIONAL & TESTED
def create_SIUID_folders(hierarchy_json,jpg_mask_overlay_directory):
    for studyUID in hierarchy_json:

        # Create a potential path for new directories.
        poten_studyUID_path = os.path.join(jpg_mask_overlay_directory, studyUID)
        
        # Create a directory that is titled after the studyUID, if the directory already exists, dont do anything. 
        os.makedirs(poten_studyUID_path, exist_ok = True)

# OPERATIONAL & TESTED
def main():

    print("------ SCRIPT EXECUTE --- DCSS V1 ------")

    # Initialize Counters
    all_jpg_frames = 0
    dicom_count = 0

    # Initialize File Paths.
    main_folder_path = os.path.dirname(os.path.abspath(__file__))
    hierarchy_path = os.path.join(main_folder_path, "Fetal_Echo_05.json")

    # Open and Load JSON File.
    with open(hierarchy_path) as hierarchy_File:
        hierarchy_json = json.load(hierarchy_File)

    # Create a directory to store all of the Study Instance UID folders if it doesnt already exist.
    jpg_mask_overlay_directory = os.path.join(main_folder_path, "Fetal-Echo-05_JPGMO")
    os.makedirs(jpg_mask_overlay_directory, exist_ok=True)

    # Create Study Instance UID Folders
    create_SIUID_folders(hierarchy_json,jpg_mask_overlay_directory)

    # Look thorugh all the Study Instance UID's in the JSON file.
    
    # Now that the Study Instance UID directories are created, move through the Excel hash file to look at the DCM file names.
    # Using the DCM file, grab the attribute that outlines the studyUID.
    # Match the studyUID to the directory, create a new directory for the DICOM ID.
    # In the DICOM ID directory, create the JPG's.
    # Optional: Maybe call FEMAS_v2 when built? Or keep it as a stand alone.

    # Read in the Excel dataframe.
    xl_path = os.path.join(main_folder_path, "Fetal_Echo_b5_dicom_hash.xlsx")
    xl_dataFrame = pd.read_excel(xl_path)

    # Grab all the DICOM ID's and put them into a list.
    dicom_ids = xl_dataFrame["dicomID"].tolist()
    
    # Grab all the DCM file names and again place into a list, get rid of the first slash in the path to avoid errors when joining.
    dcm_files = xl_dataFrame["folder"].tolist()
    
    # ------------------------------- NEW ADDITION SINCE LAST RUN 06/16/2025 -- FIXES POSSIBLE ISSUES WITH PATHS
    dcm_files = [filepath[1:] for filepath in dcm_files]

    # Assign the folder for the DCM files.
    dcm_folder = os.path.join(main_folder_path,"FetalEcho_batch5")

    # Go through all of the DCM File names.
    for i in range(len(dcm_files)):
        # Create a path to the DCM File.
        dcm_path = os.path.join(dcm_folder, dcm_files[i])
        dicom_count, all_jpg_frames += dicom_to_jpg_frames(dcm_path, jpg_mask_overlay_directory, dicom_ids[i])
    
    print("All Conversions Complete.")
    print(f"DICOM's Converted: {dicom_count}")
    print(f"JPG Frames Generated: {all_jpg_frames}")
    print("------ SCRIPT EXIT ------ DCSS V1 ------")

if __name__ == '__main__':
    main()