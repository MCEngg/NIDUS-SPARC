# usingS3.py

# Last Modified: Jun 11, 2025 - 10:33 AM
# Last Modified By: Matthew Chin

# Test Program Objectives:
# Learn and implement Boto3 to complete tasks in AWS S3 Cloud services.

import boto3

# To Access AWS, this requires credentials. Before running this script, in a LINUX terminal, run the command:
# aws configure
# and enter the requested credentials. Then after doing so, the script can be ran.

# Identify that s3 is inteded for the AWS S3 service.
s3 = boto3.client('s3')

dicom_bucket = "HARD CODE BCKET NAME"
dicom_prefix = "HARD CODE FOLDER"



s3.download_file('bucket name', 'object name', 'download path')

