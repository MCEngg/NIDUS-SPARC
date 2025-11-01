# ABDS_v1.py
# Automated Bucket Download Script Version 1.0
# 
# Last Modified: Jun 17, 2025 - 11:36 AM
# Last Modified By: Matthew Chin
# Status: Functional -- Awaiting Utilization
#
# Script Summary: 
# This script scrapes an Excel file to find the pathways required for a DICOM file in the 
# AWS bucket. The script then downloads all the files from the AWS bucket using the pathways constructed
# from the details of the Excel file.
# 
# Important Comments:
# To use this script, you must verify your credentials with AWS to access the bucket.
# This can be done by using Powershell and using the command: aws configure
# Make sure to have credentials ready.
# 
# Worst Case Scenario: O(n)
# 

# Imports
import os 
import sys
import pandas as pd
import boto3
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# OPERATIONAL & TESTED
def main():
    
    print("-------- SCRIPT EXECUTE --- ABDS V1 --------")

    print("Please select the Excel Hash File")
    xl_path = askopenfilename(title = "Excel Hash File",filetypes = [("Excel Files", "*.xlsx *.xls")])
    
    # If there is no hash file selected, exit script.
    if not xl_path:
        print("No file selected.")
        print("-------- SCRIPT EXIT ------ ABDS V1 --------")
        return
    
    bucket = input("Confirm Bucket Name (Case Sensitive): ")

    # Initialize Counter
    downloaded = 0

    # If running as an executable then put directory next to executable, otherwise use as normal script.
    if getattr(sys, 'frozen', False):
        main_path = os.path.dirname(sys.executable)
    else:
        main_path = os.path.dirname(os.path.abspath(__file__))
    # xl_path = os.path.join(main_path, xl_name)
    downloads_path = os.path.join(main_path, "DICOM Downloads")

    # Make a downloads folder.
    os.makedirs(downloads_path, exist_ok = True)

    # Initialize AWS
    s3 = boto3.client('s3')
    # bucket = "rawdicomdatascanaid"

    # Read in XL File.
    xl_dataframe = pd.read_excel(xl_path)

    # Grab Folder Locations and put into list.
    full_keys = xl_dataframe["folder"].tolist()
    full_keys = [key.lstrip("/") for key in full_keys]
    dicom_names = xl_dataframe["dicomID"].tolist()
    dicom_names = [name + ".dcm" for name in dicom_names]

    # Loop through and download the file using the full key and save it as the DICOM ID locally.
    for i in range(len(dicom_names)):
        
        # Handle errors using try/exception block.
        try:
            s3.download_file(bucket,full_keys[i],os.path.join(downloads_path,dicom_names[i]))
            downloaded += 1
        
        except Exception as e:
            print(f"ERROR: {dicom_names[i]} failed to download - {e}")

    print("Downloads Complete.")
    print(f"DICOM Files Downloaded: {downloaded}")
    print("-------- SCRIPT EXIT ------ ABDS V1 --------")

if __name__ == '__main__':
    main()