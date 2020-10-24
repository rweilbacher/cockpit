#SingleInstance Force
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

global cockpitPath = "C:\Users\Roland\Google Drive\Projects\cockpit"
global pythonPath = "C:\Users\Roland\AppData\Local\Programs\Python\Python37\pythonw.exe"

+F5::Edit ; Shift-F5 launches the current AutoHotkey script in preferred editor, else Notepad 

^F5::Reload ; Ctrl-F5 reloads the current AutoHotKey script after any edits.

!2::
FormatTime, CurrentDateTime,, yyyy-MM-dd
SendInput %CurrentDateTime%
return

ChangeFormattingToEvernoteHeader(headerLevel)
{
ClipBackup := Clipboard
SendInput ^c
Sleep 50
RunWait %pythonPath% "%cockpitPath%\evernote_header.pyw" %headerLevel%
SendInput ^v
Sleep 50
Clipboard := ClipBackup
}

ToggleEverNoteTextColor()
{
ClipBackup := Clipboard
SendInput ^c
Sleep 50
RunWait %pythonPath% "%cockpitPath%\evernote_textcolor.py"
SendInput ^v
Sleep 50
Clipboard := ClipBackup
}

^1::
ChangeFormattingToEvernoteHeader("h1")
return

^2::
ChangeFormattingToEvernoteHeader("h2")
return

^3::
ChangeFormattingToEvernoteHeader("h3")
return

^g::
ToggleEverNoteTextColor()
return

::opsy::opportunistically 
::nsy::necessarily 
::prio::priority 
::aes::aesthetic