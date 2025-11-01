# json_AR_UIDDet.py

# Last Modified: Jun 04, 2025 - 4:51 PM
# Last Modified By: Matthew Chin


# Test Program Objectives:
# Combining the operations of json_annotation_read.py and json_UID_detector.py.
# This script will open the main JSON file first to find the present UID folders. If the folder exists, the dicom imageId's are added
# to a list. The annotations JSON file is then opened and scanned to find the dicom box characteristics. A place holder has been added for any 
# image modification software that will be added.

# Important Notes:
# This program assumes that the DICOM folders exist if a UID folder exists.

import os
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches


hardcode_annotation_path = "C:/Users/thech/OneDrive/Desktop/NIDUS/Fetal Echo Project/Image Segmentation Mask Program/Fetal-Echo-05_[ANNOTATOR-DATA][ANNOTATE-SCHEMA].json"
hardcode_UID_path = "C:/Users/thech/OneDrive/Desktop/NIDUS/Fetal Echo Project/Image Segmentation Mask Program/Fetal_Echo_05.json"
hardcode_mainFolder =  "C:/Users/thech/OneDrive/Desktop/NIDUS/Fetal Echo Project/Image Segmentation Mask Program/"

uid_File = open(hardcode_UID_path)
uid_json = json.load(uid_File)

annotation_File = open(hardcode_annotation_path)
annotation_json = json.load(annotation_File)

# Presets
dicom_list = []

# For every studyUID object in the JSON file.
for studyUID in uid_json:
    # Create the potential UID path that the images will be stored in.
    potentialUID_Path = hardcode_mainFolder + studyUID

    # Check to see if that folder exists at the absolute path.
    if os.path.exists(potentialUID_Path):
        for dicom in uid_json[studyUID]:
            # Add the dicom names to the dicom list.
            dicom_list.append(dicom)

        # Since the UID folder exists, we need to dive deeper into the dicom's
        print("FOR UID: " + studyUID)
        # Iterate through the JSON list "annotation" to look for the imageID of the DICOM's.
        for object in annotation_json['annotations']:
            # If an imageId matches with a DICOM, print out the whole objects contents.
            if object["imageId"] in dicom_list:
                
                # PRINT OBJECTS
                # Nested dictionary. Look at the object contained the "annotations" list, then access the objects specific annotations 
                # under the "annotation" dictionary. Then access the "type" attribute to see if the annotation is a drawn box
                if object["annotation"]["type"] == "box":
                    
                    # DICOM BOX CONSTANTS
                    xC_TLHC = object["annotation"]["data"][0]
                    yC_TLHC = object["annotation"]["data"][1]
                    xC_BRHC = object["annotation"]["data"][2]
                    yC_BRHC = object["annotation"]["data"][3]
                    frame = object["frame"]
                    box_name = object["name"]

                    # Compile the path for the images.

                    # Find how many digits are used in the frame number.
                    frameJPG_digits = len(str(frame))
                    jpgPath = ""

                    # If we have less than 3 digits in the frame number, add the UID path, then however many 0's required to make the path a 4 digit
                    # number to the image. Then add on the frame number and JPG extension.
                    # We can now access the image using the absolute image path created.
                    if frameJPG_digits < 3:
                        jpgPath = potentialUID_Path + "/" + object["imageId"] + "/" + "0"*(4-frameJPG_digits) + str(frame) + ".jpg"
                    else:
                        jpgPath = potentialUID_Path + "/" + object["imageId"] + "/0" + str(frame) + ".jpg"  

                    # Print Box Specs
                    print("imageId: " + str(object["imageId"]))
                    print("Frame: " + str(frame))
                    print("XC_TLHC: " + str(xC_TLHC))
                    print("YC_TLHC: " + str(yC_TLHC))
                    print("XC_BRHC: " + str(xC_BRHC))
                    print("YC_BRHC: " + str(yC_BRHC))
                    print("ABS IMAGE PATH: " + jpgPath)
                    print()
                    # Note that: XC_TLHC stands for: X-Coordinate Top Left Hand Corner
                    # Note that: XC_BRHC stands for: X-Coordinate Bottom Right Hand Corner
                
                    # Currently Displays the image in a pop-up window.
                    # No modification being done here.
                    fig, ax = plt.subplots(1)
                    image = plt.imread(jpgPath)
                    plt.imshow(image)
                    rect = patches.Rectangle((xC_TLHC,yC_TLHC),(xC_BRHC-xC_TLHC),(yC_BRHC-yC_TLHC),facecolor = 'none', edgecolor = 'red', linewidth = 1)
                    ax.add_patch(rect)

                    plt.text(xC_TLHC, yC_TLHC-10, box_name,color = 'red', fontsize = 10)
                    plt.axis('off')
                    plt.show()

        dicom_list.clear()

    # Print a warning otherwise that there is no UID folder for the specific UID.
    else:
        print("Warning: There is no image folder for studyUID: " + studyUID)

    
        

# File Clean-up
uid_File.close()
annotation_File.close()