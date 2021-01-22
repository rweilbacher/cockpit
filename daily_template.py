import datetime
from os import path
import sys
import subprocess

DEBUG = False
DEBUG_DATE = "1970-01-01"
NOTEPAD_PATH = "C:\\Program Files\\Notepad++\\notepad++.exe"

TEMPLATE_FILE = "./daily_template.txt"

with open(TEMPLATE_FILE, "r") as file:
    filePath = file.readline().replace("\n", "")
    fileNameSuffix = file.readline().replace("\n", "")
    template = file.read()
    if DEBUG is True:
        date = DEBUG_DATE
    else:
        date = datetime.date.today().isoformat()
    fileName = date + " " + fileNameSuffix + ".txt"
    filePath += "\\" + fileName
    if path.exists(filePath) and DEBUG is False:
        input("File already exists!")
        sys.exit(1)
    with open(filePath, "w") as outFile:
        outFile.write(template)
    subprocess.run([NOTEPAD_PATH, filePath], check=True)
