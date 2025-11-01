# DCMAS_v1.py
# DICOM Conversion And Masking Automation Script Version 1.0
# 
# Last Modified: 07/08/2025 - 3:32 PM
# Last Modified By: Matthew Chin
# Status: Deployed
# 
# Script Summary:
# This script combines the previous FEMAS V2 and DCSS V1 scripts into one combined script, using methods
# FEMAS V3 and DCSS V2. This script requires the use of the Excel Hash File, JSON annotation and hierarchy files,
# and the main raw DICOM folder.
# This script has the user select the hash and JSON files as well as the main raw DICOM folder. The user then also gets
# to decide what name the images and masks will be stored in using the terminal. A prefix for all images is also requested.
# The script goes through the hierarchy JSON file and looks at each DICOM ID, matches it to the row in Excel and assigns the
# identifier link. The DICOM is then taken to be converted into JPG frames. FEMAS V3 is then prompted after every DICOM is converted.
# 
# Important Comments:
# This file can be run as an executable or it can be run in an IDE.
#
# Worst Case Scenario: O(n^3)
# 
# THIS SCRIPT IS NOT COMPLETELY EFFICIENT. This script does not take advantage of parallel processing.
# With a data set of ~100 DCM files, each producing around 200-500 JPG frames, the process took ~1 hour to complete JPG conversions.
# The masking portion took less time at ~30 minutes.
#
# DISCLAIMER!
# Portions of this script is material provided by ChatGPT. This script is optimized according to advice provided by ChatGPT.
# 

# System & File Imports
import os
import json
import sys

# DICOM Conversion Imports 
import numpy as np
import pydicom

# Image Imports
from PIL import Image
import cv2

# Excel File Imports
import pandas as pd

# GUI Imports
from tkinter import Tk
from tkinter import filedialog

# OPERATIONAL & TESTED
def normalize_pixel_array(arr):
    # We need to normailze the array to 8 bits instead of the standard 16 bits for DICOM files.
    arr = arr.astype(np.float32)
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val - min_val == 0:
        return np.zeros(arr.shape, dtype=np.uint8)
    arr = (arr - min_val) / (max_val - min_val) * 255.0
    return arr.astype(np.uint8)

# OPERATIONAL & TESTED
def dicom_to_jpg(p_num, d_num, prefix, dicom_path, jpg_directory, dicom_id):
    # Load the DICOM file.
    dcm = pydicom.dcmread(dicom_path)

    # Check if it’s a multi-frame image or single image.
    if hasattr(dcm, 'PixelData'):

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
                img.save(os.path.join(jpg_directory, f"{prefix}_P{p_num}D{d_num}_{i:04d}.jpg"))
        else:
            # Single-frame DICOM.
            frame = dcm.pixel_array
            frame_normalized = normalize_pixel_array(frame)
            img = Image.fromarray(frame_normalized)
            img.save(os.path.join(jpg_directory, f"{prefix}_P{p_num}D{d_num}_0000.jpg"))
        print(f"Converted {dicom_id} to JPGs.")
    else:
        print("No pixel data found in the DICOM file.")
    
    return getattr(dcm,'NumberOfFrames',1)

# OPERATIONAL & TESTED
def masks(vertices, height, width, image, mask_path, overlay_path):
    # AI Generated Code
    # Create the array of zeros using the height and width of the image (in pixels).
    mask = np.zeros((height, width), dtype = np.uint8)

    # Fill in a polygon using the vertices found before and colour them white.
    cv2.fillPoly(mask, [vertices], 255)

    # Overlay the mask onto a copy of the image.
    # overlay = image.copy()
    # overlay[mask == 255] = [0, 0, 255]
    # overlaid_image = cv2.addWeighted(overlay, 0.5, image, 0.5, 0)

    # Save the Mask & Overlay Using ABS Paths
    # cv2.imwrite(mask_path, mask)
    success = cv2.imwrite(mask_path, mask)
    if not success:
        print(f"[ERROR] Failed to save mask: {mask_path}")
        # continue

    # cv2.imwrite(os.path.join(overlay_path, jpg_name), overlaid_image)
    return

# OPERATIONAL & TESTED
def run_DCSSV2(main_folder_path,xl_dataframe,xl_path,prefix):
    
    # Initialize Counters
    all_jpg_frames = 0
    dicom_count = 0

    # Get the user to select which JSON file.
    print("Please select the JSON Hierarchy file.")
    hierarchy_path = filedialog.askopenfilename(title = "JSON Hierarchy File", filetypes = [("JSON File", "*.json")])
    
    if not hierarchy_path:
        print("No hierarchy JSON file selected.")
        print("------ SCRIPT EXIT ------ DCMAS V1 ------")
        return
    
    # Open and Load JSON File.
    with open(hierarchy_path) as hierarchy_File:
        hierarchy_json = json.load(hierarchy_File)

    
    # Create the main directory for images and masks.
    jpg_name = input("What would you like to name the JPG image folder?: ")
    jpg_directory = os.path.join(main_folder_path, jpg_name)
    os.makedirs(jpg_directory, exist_ok=True)

    # Get the folder where the DICOM's are stored.
    print("Please select the master DICOM folder.")
    dicom_folder = filedialog.askdirectory(title = "Select the main DICOM folder.")

    if not dicom_folder:
        print("DICOM folder not selected.")
        print("------ SCRIPT EXIT ------ DCMAS V1 ------")
        return

    dicom_ids = xl_dataframe["dicomID"].tolist()
    dcm_path = xl_dataframe["folder"].tolist()
    dcm_path = [path[1:] for path in dcm_path]

    # Initialize P# and D#
    p_num = 1
    d_num = 1

    dicom_lookup = {dicom_ids[i]: dcm_path[i] for i in range(len(dicom_ids))}
    dicom_control = 0

    if 'Identifier' not in xl_dataframe.columns:
        xl_dataframe['Identifier'] = ""
    xl_dataframe['Identifier'] = xl_dataframe['Identifier'].astype(str)

    # Go through all study instances.
    for study in hierarchy_json:
        
        # Go through all DICOM's contained in a study.
        for dicom_id in hierarchy_json[study]:

            # If the DICOM ID is in the list, find the path at the same index.
            if dicom_id in dicom_ids:
                dicom_path = dicom_lookup.get(dicom_id)

                # Call the convert function.
                all_jpg_frames += dicom_to_jpg(p_num, d_num, prefix, os.path.join(dicom_folder,dicom_path),jpg_directory,dicom_id)
                
                # Update the Excel Sheet with the Patient# and DICOM# for references.
                xl_dataframe.loc[dicom_control, 'Identifier'] = f"P{p_num}D{d_num}" 
                dicom_count += 1
                
            else:
                print(f"Warning! DICOM: {dicom_id} not found in Excel File. Skipping file.")
                xl_dataframe.loc[dicom_control, 'Identifier'] = "ERROR - File Not Converted"
        
            dicom_control += 1
            d_num += 1

        p_num += 1
        d_num = 1

    xl_dataframe.to_excel(xl_path, index = False)

    print()
    print("All Conversions Complete.")
    print(f"DICOM's Converted: {dicom_count}")
    print(f"JPG Frames Generated: {all_jpg_frames}")
    print()
    return jpg_directory

# OPERATIONAL & TESTED
def run_FEMASV3(main_folder_path, xl_dataframe,prefix,img_directory):

    mask_name = input("What would you like to name the mask folder?: ")
    mask_directory = os.path.join(main_folder_path,mask_name)
    os.makedirs(mask_directory, exist_ok = True)

    # Continue with mask generation.
    print("Please select the annotation JSON file.")
    annotation_path = filedialog.askopenfilename(title = "JSON Annotation File", filetypes = [("JSON File", "*json")])

    if not annotation_path:
        print("No annotation JSON file was selected.")
        print("------ SCRIPT EXIT ------ DCMAS V1 ------")
        return
    
    # Open and load annotations file.
    with open(annotation_path) as annotation_file:
        annotation_json = json.load(annotation_file)

    # Initialize the Identifiers and DICOM ID lists.
    identifiers = xl_dataframe['Identifier'].tolist()
    dicom_ids = xl_dataframe['dicomID'].tolist()

    identifier_lookup = {dicom_ids[i] : identifiers[i] for i in range(len(dicom_ids))}

    # Go through all the annotations.
    for entry in annotation_json['annotations']:

        # Variable to help determine which mask.
        mask_type = entry['annotation']['type']

        # If an entry matches a DICOM ID and is a box or polygon, create the mask.
        if (entry['imageId'] in dicom_ids) and (mask_type == "box" or mask_type == "polygon"):
            identifier = identifier_lookup.get(entry["imageId"])
            img_name = f"{prefix}_{identifier}_{entry['frame']:04d}.jpg" 
            mask_path = os.path.join(mask_directory,img_name)
            jpg_path = os.path.join(img_directory,img_name)

            image = cv2.imread(jpg_path)

            # If the path doesnt exist.
            if image is None:
                raise FileNotFoundError(f"No Corresponding JPG : {img_name}")
            
            height, width = image.shape[:2]

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
            masks(vertices_array, height, width, image, mask_path, None)
    
    print()
    print("Mask Generation Complete.")
    

def main():
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)

    # Initialize main path.
    if getattr(sys, 'frozen', False):
        main_folder_path = os.path.dirname(sys.executable)
    else:
        main_folder_path = os.path.dirname(os.path.abspath(__file__))

    print("------ SCRIPT EXECUTE --- DCMAS V1 ------")

    # Get the user to select the Excel file.
    print("Please select the Excel Hash File.")
    xl_path = filedialog.askopenfilename(title = "Excel Hash File", filetypes = [("Excel Hash File", ("*.xlsx", "*.xls"))])

    if not xl_path:
        print("No Excel file selected.")
        print("------ SCRIPT EXIT ------ DCMAS V1 ------")
        return
    
    # Load the Excel dataframe.
    xl_dataframe = pd.read_excel(xl_path)

    # Get the prefix for the desired naming convention.
    print()
    print("Image files will follow the naming convention: [prefix]_P[x]D[x]_[frame#].jpg.\nEx. [prefix]_P1D1_0000.jpg")
    prefix = input("Please indicate what prefix was/should be used for this batch: ")
    
    print()
    print("Which operation would you like to use?\n1.DICOM to JPG Conversion (DCSS)\n2.Mask Generation (FEMAS)")
    program_choice = input()

    if program_choice == "1":
        jpg_direc = run_DCSSV2(main_folder_path,xl_dataframe,xl_path,prefix)

        # Ask to generate masks
        decision = input("Generate Masks? (Y/N): ")
        if(decision.lower() != "y"):
            print("------ SCRIPT EXIT ------ DCMAS V1 ------")
            return
        
        run_FEMASV3(main_folder_path,xl_dataframe,prefix,jpg_direc)

    elif program_choice == "2":
        print("Please select the master JPG image folder:")
        jpg_direc = filedialog.askdirectory(title = "Master JPG Image Folder")
        run_FEMASV3(main_folder_path,xl_dataframe,prefix,jpg_direc)

    
    print("------ SCRIPT EXIT ------ DCMAS V1 ------")
    input()

if __name__ == "__main__":
    main()