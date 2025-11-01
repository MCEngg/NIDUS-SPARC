# impRW.py

# Last Modified: Jun 11, 2025 - 1:12 PM
# Last Modified By: Matthew Chin

# Test Program Objectives:
# Read through a JSON file and write content to an excel file. Then read from the excel file to
# combine the pathways together.

import os
import json
import pandas as pd
from openpyxl import load_workbook

# Set up paths for every file
curr_folder = os.path.dirname(os.path.abspath(__file__))

excel = "pathways.xlsx"
xl_path = os.path.join(curr_folder, excel)

UID_path = os.path.join(curr_folder, "Fetal_Echo_05_test.json")

# Open and load the JSON file
with open(UID_path) as uid_File:
    uid_json = json.load(uid_File)

# For every study UID
# for studyUID in uid_json:
    
#     # And for every DICOM ID contained in it
#     for i in range(len(uid_json[studyUID])):
        
#         # Read the excel file for the latest changes
#         pre_exist = pd.read_excel(xl_path, sheet_name = 0, header = 0)
#         # Create the new data frame with the studyId and the dicomId
#         new_data_frame = pd.DataFrame({'STUDY ID' : [studyUID], 'DICOM ID' : [uid_json[studyUID][i]]})
#         # Combine the new data with the original data using the concat method
#         combined_data = pd.concat([pre_exist, new_data_frame], ignore_index = True)
#         # Write to the excel file using the newly combined data frame
#         with pd.ExcelWriter(xl_path, mode = 'a', engine = 'openpyxl', if_sheet_exists = 'replace') as writer:
#             combined_data.to_excel(writer,sheet_name = 'Sheet1', index = False)

# THIS IS ACTUALLY SUPER SLOW! 
# Why re-read and re-write every single time? What about reading once and writing once and combining the data frames only one?
# More efficient code:

new_rows = []

for studyUID in uid_json:
    for i in range(len(uid_json[studyUID])):
        new_rows.append({'STUDY ID' : studyUID, 'DICOM ID' : uid_json[studyUID][i]})

pre_exist = pd.read_excel(xl_path, sheet_name = 0, header = 0)
new_data_frame = pd.DataFrame(new_rows)
combined_data = pd.concat([pre_exist, new_data_frame], ignore_index = True)

with pd.ExcelWriter(xl_path, mode = 'a', engine = 'openpyxl', if_sheet_exists = 'replace') as writer:
    combined_data.to_excel(writer,sheet_name = 'Sheet1', index = False)

# Note that this next step is extremely inefficient! This is only used for learning and should not be implemented.
# This next section will read the excel file and combine its contents to create another pathway and will then 
# write back to excel file but in a different column


sheet1 = pd.read_excel(xl_path, sheet_name = 0, header = 0)
combined_paths = []
for i in range(len(sheet1['STUDY ID'])):
    combined_paths.append(sheet1['STUDY ID'][i] + "/" + sheet1['DICOM ID'][i])
sheet1['COMBINED'] = combined_paths
sheet1.to_excel(xl_path, index = False)