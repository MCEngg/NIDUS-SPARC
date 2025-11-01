# FEMAS_v1.3.py
# Fetal Echo Mask Automation Script Version 1.3
#
# Last Modified: Jun 10, 2025 - 1:29 PM
# Last Modified By: Matthew Chin
# Status: Deployed -- New Version Available
#
# Script Summary:
# This script creates a mask image and an overlayed image of rectangles and polygons on top of the original image. These images are then saved to the
# same DICOM folders where the original images could be found.
#
# Important Comments:
# This file should be kept in the same directory as the [ANNOTATOR-DATA][ANNOTATE-SCHEMA].json file, the Fetal Echo JSON file, and the 
# study folders that hold the DICOM folders.
# The JSON files are hardcoded into this file and require manual manipulation.
#
# Worst Case Scenario: O(n^2)
# 
# DISCLAIMER!
# A portion of this code was written by ChatGPT! Comments were put in place to help explain the operations. This helps with learning what the script
# is doing for future development!
#
# To Run the File:
# There are 2 ways to run this script. Either through an IDE and by pressing the play button or by going through a terminal (LINUX UBUNTU was used to create this one).
#
# To run this script through LINUX:
# 1. Navigate to the directory where this script is located along with the JSON files (see above for more details)
# 2. Create a virtual environment for Python
# 	- python3 -m venv ~/femas-venv
# 3. Activate the virtual environment
# 	- source ~/femas-venv/bin/activate
# 4. Install any libraries that are required for the script (if not already installed)
# 	- pip install numpy
# 	- pip install opencv-python
# 5. Run the script
# 	- python3 ./femas.py

# Imports
import os
import json
import numpy as np
import cv2


def masks_and_overlays(vertices, height, width, image, saveDirectory, jpg_name):
    # AI Generated Code 
    # Create the array of zeros using the height and width of the image (in pixels).
    mask = np.zeros((height, width), dtype = np.uint8)

    # Fill in a polygon using the verticies found before and colour them white.
    cv2.fillPoly(mask, [vertices], 255)
    
    # Overlay the mask onto a copy of the image.
    overlay = image.copy()
    overlay[mask == 255] = [0, 0, 255]
    overlaid_image = cv2.addWeighted(overlay, 0.5, image, 0.5, 0)
    
    # Save the Mask & Overlay Using ABS Paths
    cv2.imwrite(os.path.join(saveDirectory, "Overlaid_" + jpg_name), overlaid_image)
    cv2.imwrite(os.path.join(saveDirectory, "Mask_" + jpg_name), mask)

    # Display the Mask & Overlay (OPTIONAL TO TURN OFF)
    # cv2.imshow('Binary Mask', mask)
    # cv2.imshow('Overlayed Mask', overlaid_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


def main():
    # Initialize Folder and File Paths.
    femas_folder_path = os.path.dirname(os.path.abspath(__file__))
    annotation_path = os.path.join(femas_folder_path, "Fetal-Echo-05_[ANNOTATOR-DATA][ANNOTATE-SCHEMA].json")
    UID_path = os.path.join(femas_folder_path, "Fetal_Echo_05.json")

    # Open and Load the JSON files for use. Files will automatically close after scope ends.
    with open(UID_path) as uid_File:
        uid_json = json.load(uid_File)

    with open(annotation_path) as annotation_File:
        annotation_json = json.load(annotation_File)

    # For every studyUID object in the JSON file.
    for studyUID in uid_json:
        
        # Create the potential UID path that the images will be stored in.
        potentialUID_Path = os.path.join(femas_folder_path, studyUID)

        # Check to see if that folder exists at the absolute path.
        if os.path.exists(potentialUID_Path):
            
            dicom_list = uid_json[studyUID]

            # Iterate through the JSON list 'annotation' to look for the imageID of the DICOM's.
            for object in annotation_json['annotations']:
                
                # If an imageId matches with a DICOM, investigate image data.
                if object['imageId'] in dicom_list:

                    # Compile Image Paths
                    jpgImage_name = "0"*(4-len(str(object['frame']))) + str(object['frame']) + ".jpg"
                    jpgPath = os.path.join(potentialUID_Path, object['imageId'], jpgImage_name)
                    image = cv2.imread(jpgPath)

                    # If Path doesn't exist.
                    if image is None:
                        raise FileNotFoundError("DICOM Frame Not Found! Check Path.")
                    
                    height, width = image.shape[:2]
                    
                    # Save Directory for The Masks & Overlays
                    saveDirectory = os.path.join(femas_folder_path, potentialUID_Path, object['imageId'])


                    # Polygon Masks
                    if object['annotation']['type'] == "polygon":
                        
                        # AI Generated Code:
                        # Take the annotation data and convert into an array of integers. Then reshape the array so that consecutive coordinates 
                        # are paired together. The resulting array is an array of coordinate pairs that represent the polygon vertices.
                        vertices_array = np.array(object['annotation']['data'], dtype = np.int32).reshape((-1,1,2))
                        
                        # Create And Save Masks & Overlays
                        masks_and_overlays(vertices_array,height,width,image,saveDirectory,jpgImage_name)


                    # Box Masks
                    if object['annotation']['type'] == "box":
                        
                        # Top Left Hand Corner (TLHC)
                        x_LeftTop = int(object['annotation']['data'][0])
                        y_LeftTop = int(object['annotation']['data'][1])
                        
                        # Bottom Right Hand Corner (BRHC)
                        x_RightBottom = int(object['annotation']['data'][2])
                        y_RightBottom = int(object['annotation']['data'][3])
                        
                        # AI Generated Code:
                        vertices_array = np.array([[x_LeftTop,y_LeftTop],[x_RightBottom,y_LeftTop],[x_RightBottom,y_RightBottom],[x_LeftTop,y_RightBottom]]).reshape((-1,1,2))

                        # Create And Save Masks & Overlays
                        masks_and_overlays(vertices_array,height,width,image,saveDirectory,jpgImage_name)
            
            dicom_list.clear()

        # Print a warning that there is no UID folder for the specific UID.
        else:
            print("Warning: There is no study folder for studyUID: " + studyUID)

if __name__ == '__main__':
    main()