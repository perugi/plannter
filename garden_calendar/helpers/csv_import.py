# A simple helper function to import data into the Plant table from a csv file
import csv
import sys
import os
import django

sys.path.append("/mnt/data/Domo/Tech/Python/projects/plannter")
os.environ["DJANGO_SETTINGS_MODULE"] = "plannter.settings"
django.setup()

from garden_calendar.models import Plant, User

if len(sys.argv) != 2:
    print("Usage: python3 csv_import.py input.csv ")
    sys.exit()


with open(sys.argv[1], "r") as input_file:
    reader = csv.reader(input_file, delimiter=",")
    next(reader, None)  # skip the headers
    for row in reader:
        plant = {}
        plant["id"] = int(row[0])
        plant["creator"] = User.objects.get(pk=int(row[1]))
        plant["name_si"] = row[2]
        plant["name_en"] = row[3]
        plant["todos"] = ",".join(row[4:])

        plant_item = Plant(
            id=plant["id"],
            creator=plant["creator"],
            name_si=plant["name_si"],
            name_en=plant["name_en"],
            todos=plant["todos"],
        )
        plant_item.save()

print("Finished...")
