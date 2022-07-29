# A simple helper function to generate the header of a .csv file (for SQL import)

import csv
import sys

if len(sys.argv) not in [2, 3]:
    print("Usage: python3 csv_styler.py [input.csv] output.csv")
    sys.exit()

# If the user does not specify an input file, an output file with only the title row will be generated.
if len(sys.argv) == 2:
    output_file = open(sys.argv[1], "w")
else:
    output_file = open(sys.argv[2], "w")
writer = csv.writer(output_file, delimiter=",")

# Create the title row
title_row = ["id", "user_id", "name"]
for i in range(1, 13):
    for j in range(1, 4):
        title_row.append(f"todo_{i}-{j}")

writer.writerow(title_row)

if len(sys.argv) == 3:
    input_file = open(sys.argv[1], "r")
    reader = csv.reader(input_file, delimiter=",")

    for row in reader:
        # Change the 'N' to '', signifying no work with the plant
        row_new = []
        for element in row:
            if element == "N":
                row_new.append("")
            else:
                row_new.append(element)
        writer.writerow(row_new)

    input_file.close()

output_file.close()

print("Finished...")
