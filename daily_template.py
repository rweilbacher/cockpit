import datetime
from os import path
import sys

TEMPLATE_FILE = "./daily_template.txt"

with open(TEMPLATE_FILE, "r") as file:
    filePath = file.readline().replace("\n", "")
    fileNameSuffix = file.readline().replace("\n", "")
    template = file.read()
    date = datetime.date.today().isoformat()
    fileName = date + " " + fileNameSuffix + ".txt"
    if path.exists(filePath + "\\" + fileName):
        input("File already exists!")
        sys.exit(1)
    with open(filePath + "\\" + fileName, "w") as outFile:
        outFile.write(template)