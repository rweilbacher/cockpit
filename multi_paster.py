import subprocess

INPUT_FILE = "input.txt"
# This name cannot contain any spaces or shell metacharacters like : or \
OUTPUT_FILE = "multi_paster.ahk"
AHK_PATH = "C:\Program Files\AutoHotkey\AutoHotkey.exe"

ahkHeader = """#SingleInstance Force
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
"""

ahkTemplate = """
!{0}::
Send, {1}
return
"""


with open(INPUT_FILE, 'r') as inputFile, open(OUTPUT_FILE, 'w') as outputFile:
    data = inputFile.read().split("\n")
    outputFile.write(ahkHeader)
    for idx in range(0, len(data)):
        print("Alt + " + str(idx + 1) + ": " + data[idx])
        hotkey = ahkTemplate.format(str(idx + 1), data[idx])
        outputFile.write(hotkey)

# subprocess.run([AHK_PATH, OUTPUT_FILE], check=True)
process = subprocess.Popen([AHK_PATH, OUTPUT_FILE])

print("\nHit Enter to exit")
input()
process.terminate()