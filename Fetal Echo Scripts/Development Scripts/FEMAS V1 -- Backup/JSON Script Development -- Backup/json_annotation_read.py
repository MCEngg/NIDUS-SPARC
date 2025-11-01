#json_annotation_read.py

# Last Modified: Jun 04, 2025 - 1:06 PM
# Last Modified By: Matthew Chin

# Test Program Objectives:
# Using test_dicom hardcodes, print out any occurance of a "box" and its respective attributes.
# All "Annotation" objects are in the list "Annotations".
# This test program can only handle boxes and not brushes as of 06-04-2025.

import json
hardcode_local_path = 'C:/Users/thech/OneDrive/Desktop/NIDUS/Fetal Echo Project/Image Segmentation Mask Program/Fetal-Echo-05_[ANNOTATOR-DATA][ANNOTATE-SCHEMA].json'

json_file = open(hardcode_local_path)
json_data = json.load(json_file)

dicom_list = ["dicom-6354a6s4d35asd886qw645afe4a","dicom-684qwe654a56sdf6weqf","dicom-3218asrasdgq5e98735a"]

# Iterate through the JSON list "annotation" to look for the imageID of the DICOM's.
for object in json_data['annotations']:
    # If an imageId matches with a DICOM, print out the whole objects contents.
    if object["imageId"] in dicom_list:
        
        # PRINT OBJECTS
        # Nested dictionary. Look at the object contained the "annotations" list, then access the objects specific annotations under the "annotation" dictionary. Then access the "type" attribute
        # to see if the annotation is a drawn box
        if object["annotation"]["type"] == "box":
            
            # DICOM BOX CONSTANTS
            frame = 0

            # X & Y Coordinates of the left hand corner of the box.
            xbox_LHC = 0
            ybox_LHC = 0

            # Height & Width of the box.
            box_height = 0
            box_width = 0


            # Load box specs.
            xbox_LHC = object["annotation"]["data"][0]
            ybox_LHC = object["annotation"]["data"][1]
            box_height = object["annotation"]["data"][2]
            box_width = object["annotation"]["data"][3]
            frame = object["frame"]

            # Print Box Specs
            print("imageId: " + str(object["imageId"]))
            print("Frame: " + str(frame))
            print("XC_LHC: " + str(xbox_LHC))
            print("YC_LHC: " + str(ybox_LHC))
            print("Box Height: " + str(box_height))
            print("Box Width: " + str(box_width))
            print()

json_file.close()