# excelReadWrite.py

# Last Modified: Jun 11, 2025 - 10:10 AM
# Last Modified By: Matthew Chin

# Test Program Objectives:
# Be able to read and write to an excel file and to store information in Python lists retrieved from the Excel file.

import pandas as pd
import os

# Read Data from Excel file that only has 1 sheet
# curr_path = os.path.dirname(os.path.abspath(__file__))
# excel_path = os.path.join(curr_path, "Tester.xlsx")
# data_frame = pd.read_excel(excel_path)

# print(data_frame)
# print()
# print(data_frame['Name'])
# print()
# print(data_frame['Name'][1] + " is taking classes for a degree in: " + data_frame['Degree'][1])



# Read Data from Excel file that has multiple sheets

dir_path = os.path.dirname(os.path.abspath(__file__))
file_name = "Tester.xlsx"
file_path = os.path.join(dir_path, file_name)

sheet1 = pd.read_excel(file_path, sheet_name = 0, header = 0)

# The header option in this line indicates that there is no labels in the columns of the sheet, so the contents can be accessed using typical list/array methods.
sheet2 = pd.read_excel(file_path, sheet_name = 1, header = None)

# Prints the second name under the 'Name' column (remember index starts at 0)
print(sheet1['Name'][1])
print()

# Prints the age of the second person, the first index relates to the first column, the second index relates to the second row (index starts at 0)
print(sheet2[1][1])




# Writing to an Excel sheet

# Create new data to append (in the form of a dictionary): 
new_data_frame = pd.DataFrame({'Name' : ['Alec Bilan'], 'Age' : [25], 'Degree': ['Mechanical Engineering']})

# Combine the data frames using the concat method
combined_data = pd.concat([sheet1, new_data_frame], ignore_index = True)

# Overwrite the street with uploaded data
with pd.ExcelWriter(file_path, mode = 'a', engine = 'openpyxl', if_sheet_exists = 'replace') as writer:
    combined_data.to_excel(writer,sheet_name = 'Sheet1', index = False)

# Note that the mode specifies append mode ('a')    
# The index specification when set to False makes sure that the indexes are not saved as an extra column in the file



# Writing to a specific cell
# from openpyxl import load_workbook
# workbook = load_workbook(xl_path)
# worksheet = workbook['Sheet1']
# worksheet['C1'] = 'Combined Paths'
# workbook.save(xl_path)



# Deleting Data
# To delete data we can use the .drop method in conjunction with the dataframe
# df = df.drop('Age', axis=1)  # This deletes a whole column (the age column), axis = 1 specifies the column and not the row (which is 0)
# Note that instead of using the label we can also use indices

# We can also drop multiple rows or columns using a list
# df = df.drop(['Age','Degree'], axis = 1) # Droping multiple columns using labels
# df = df.drop([0,2], axis = 0) # Dropping multiple rows

# We can also delete rows based on a condition for a column
# df = df[df['Age'] >= 20] # This filters out any rows that dont meet the condition

# To remove duplicate rows we can use
# df = df.drop_duplicates()
# OR
# df = df.drop_duplicates(subset = 'Name') # The subset is the name of a specific column to drop duplicates

# To Delete the whole dataframe:
# We simply use the del operator
# del data_frame