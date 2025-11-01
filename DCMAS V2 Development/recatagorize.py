# recatagorize.py
#
# Last Modified: 07/09/2025
# Last Modified By: Matthew Chin
# Status: In Development

import os
from tkinter import filedialog, Tk
import shutil
import pandas as pd
import json

def main():
    Tk().withdraw()

    img_or_mask_folder = filedialog.askdirectory(title="Select the img or mask folder")

    excel_hash = filedialog.askopenfilename(title="Please select the hash file")
    xl_dataframe = pd.read_excel(excel_hash)

    json_path = filedialog.askopenfilename(title="Please select the JSON file")
    with open(json_path) as json_file:
        json_data = json.load(json_file)

    count = 0

    # Go through all annotations
    for annotation in json_data['annotations']:

        if isinstance(annotation['annotation']['data'], list):
            # Get DICOM image ID
            dicom_id = annotation['imageId']
            
            # Get identifier form xl
            identifier_row = xl_dataframe.loc[xl_dataframe['dicomID'] == dicom_id]
            identifier = identifier_row.iloc[0][3]

            # Get frame# in format 
            frame = f"{annotation['frame']:04d}"

            designator = f"{identifier}_{frame}"

            classification = annotation['name']
            new_folder = os.path.join(img_or_mask_folder, classification)
            

            files = os.listdir(img_or_mask_folder)

            for filename in files:
                source = os.path.join(img_or_mask_folder, filename)
                destination = os.path.join(new_folder, filename)

                if designator in filename and os.path.isfile(source):
                    os.makedirs(new_folder, exist_ok = True)
                    shutil.move(source,destination)
                    print(f"Moved: {designator} to {classification}")
                    count += 1

    print(f"Moved {count} files")       

               
if __name__ == "__main__":
    main()