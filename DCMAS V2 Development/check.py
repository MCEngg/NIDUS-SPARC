
import json
import os
import tkinter as Tk
from tkinter import filedialog

hardcode_local_path = filedialog.askopenfilename()

json_file = open(hardcode_local_path)
json_data = json.load(json_file)

# Iterate through the JSON list "annotation" to look for the imageID of the DICOM's.
for object in json_data['annotations']:

    # PRINT OBJECTS
    # Nested dictionary. Look at the object contained the "annotations" list, then access the objects specific annotations under the "annotation" dictionary. Then access the "type" attribute
    # to see if the annotation is a drawn box
    if isinstance(object['annotation']['data'],list):
        print(object['name'])
        

json_file.close()

# something = []
# if (isinstance(something, list)):
#     print("Hello!")
# else:
#     print("Nope")