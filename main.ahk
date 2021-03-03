﻿#SingleInstance Force
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
; ! = Alt
; ^ = Ctrl
; # = Win
; + = Shift
; <> = Left or right version
; * = Wildcard
; ::hw::Hello World = Text expansion
; $ prefix disables activation of the hotkey by its own Send commands

; global variable to enable and disable custom Evernote hotkeys, since they might clash with other applications
global enableEvernote = false

; Find python3 based on PATH variable
EnvGet, envPath, PATH
splitPath := StrSplit(envPath, ";")
global pythonPath = ""
Loop % splitPath.MaxIndex() 
{
	currPath := splitPath[A_Index]
	found := RegExMatch(currPath, "[p|P]ython3.\\?$")
	if (found != 0) {
		global pythonPath = currPath
	}
}
		
global DE_KEY_LAYOUT = 0x4070407
global EN_KEY_LAYOUT = 0x4090409

; Hotkeys that make small changes and reloads much faster
+F5::Edit ; Shift-F5 launches the current AutoHotkey script in preferred editor, else Notepad
^F5::Reload ; Ctrl-F5 reloads the current AutoHotKey script after any edits.

; --- Helper functions ---

join(sep, params*) {
    for index,param in params
        str .= param . sep
    return SubStr(str, 1, -StrLen(sep))
}

; Execute a python script
; @param path The path to the python script
; @param console true if console should be enabled, false if not
; @param args* command line parameters that will be passed to the python script
runPythonScript(path, console, args*) {
	if (pythonPath = "") {
		MsgBox Can't execute python script because python3 was not found in PATH variable
		return
	}
	pythonExec := pythonPath
	if (console = true) {
	    pythonExec .= "\python.exe"
	}
	else {
	    pythonExec .= "\pythonw.exe"
	}
    argsString := join(" ", args*)
    RunWait %pythonExec% %path% %argsString%,, UseErrorLevel
    if (ErrorLevel != 0) {
        MsgBox, python script %path% encountered an error!
    }
}

; --- General hotkeys ---

; Send the current date in ISO format
!2::
FormatTime, CurrentDateTime,, yyyy-MM-dd
SendInput %CurrentDateTime%
return

; Start the templates python script, which is a small GUI for selecting templates to load into the Clipboard
!F2::
runPythonScript(".\templates.py", false)
return

!F3::
Hotkey, !2, Off
runPythonScript(".\multi_paster.py", true)
Hotkey, !2, On
return

!F10::
runPythonScript(".\pihole_blocker.py", false)
return

!F11::
runPythonScript(".\willpower_timer.py", false)
return

!F5::
runPythonScript(".\daily_template.py", true)
return

; --- Evernote Utils ---

changeFormattingToEvernoteHeader(headerLevel)
{
Send, {SHIFT}+{Home}
Sleep 30
ClipBackup := Clipboard
SendInput ^c
Sleep 30
runPythonScript(".\evernote_header.pyw", false, headerLevel)
SendInput ^v
Sleep 30
Clipboard := ClipBackup
}

toggleEverNoteTextColor()
{
ClipBackup := Clipboard
SendInput ^c
Sleep 50
runPythonScript(".\evernote_textcolor.py", false)
SendInput ^v
Sleep 50
Clipboard := ClipBackup
}

!F12::
if (enableEvernote = true) {
    global enableEvernote = false
	MsgBox, Disabled Evernote hotkeys
}
else {
    global enableEvernote = true
	MsgBox, Enabled Evernote hotkeys
}
return

$^0::
if (enableEvernote = false) {
    Send, ^0
    return
}
changeFormattingToEvernoteHeader("0")
return

$^1::
if (enableEvernote = false) {
    Send, ^1
    return
}
changeFormattingToEvernoteHeader("1")
return

$^2::
if (enableEvernote = false) {
    Send, ^2
    return
}
changeFormattingToEvernoteHeader("2")
return

$^3::
if (enableEvernote = false) {
    Send, ^3
    return
}
changeFormattingToEvernoteHeader("3")
return

$^g::
if (enableEvernote = false) {
    Send, ^g
    return
}
toggleEverNoteTextColor()
return

; --- Reduce strain on right hand ---

; Find out the ID of the current keyboard layout
; I often switch between German and English
getInputLocaleId()
{
SetFormat, Integer, H
  WinGet, WinID,, A
  ThreadID:=DllCall("GetWindowThreadProcessId", "UInt", WinID, "UInt", 0)
  InputLocaleID:=DllCall("GetKeyboardLayout", "UInt", ThreadID, "UInt")
  return InputLocaleID
}

; Alternative Mouse scroll to reduce strain on right hand
!s::
Click WheelDown
return		

; Alternative Mouse scroll to reduce strain on right hand
!w::
Click WheelUp
return	

; Alternative Enter to reduce strain on right hand
!q::
Send, {Enter}
return

; Alternative Backspace to reduce strain on right hand
; ö and ` have the same keycode and I regularly switch layouts, so hotkey depends on keyboard layout
$`::
inputLocaleId := getInputLocaleId()
if (inputLocaleId = EN_KEY_LAYOUT) {
    Send, {Backspace}
}
else if (inputLocaleId = DE_KEY_LAYOUT) {
    Send, ö
}
return
														
; --- Word expansions ---

::opsy::opportunistically 
::nsy::necessarily 
::prio::priority 
::aes::aesthetic
::delib::deliberately
::consc::consciousness
::conscy::consciously
::dont::don't
::doesnt::doesn't
::cant::can't
::wont::won't
::havent::haven't
::couldnt::couldn't
::wouldnt::wouldn't
::wasnt::wasn't
::didnt::didn't
::imt::important
::assu::assumption
::urose::purpose
::andre::andré
::bjoern::björn