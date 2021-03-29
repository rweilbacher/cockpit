import datetime
from os import path
import calendar
import sys
import subprocess


DEBUG = False
DEBUG_DATE = datetime.date(1970, 1, 1)
NOTEPAD_PATH = "C:\\Program Files\\Notepad++\\notepad++.exe"

TEMPLATE_FILE = "./daily_template.txt"

if len(sys.argv) > 1:
    dayOffset = int(sys.argv[1])
else:
    dayOffset = 0

if DEBUG is True:
    date = DEBUG_DATE + datetime.timedelta(days=dayOffset)
else:
    date = datetime.date.today() + datetime.timedelta(days=dayOffset)
weekday = calendar.day_name[date.weekday()]
isoDate = date.isoformat()

with open(TEMPLATE_FILE, "r") as file:
    filePath = file.readline().replace("\n", "")
    fileNameSuffix = file.readline().replace("\n", "")
    template = file.read()
    fileName = isoDate + "_" + weekday + "_" + fileNameSuffix + ".txt"
    filePath += "\\" + fileName
    if path.exists(filePath):
        subprocess.run([NOTEPAD_PATH, filePath], check=True)
    with open(filePath, "w") as outFile:
        outFile.write(template)
    subprocess.run([NOTEPAD_PATH, filePath], check=True)
