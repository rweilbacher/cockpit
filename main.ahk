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

SendEvernoteHeader(headerLevel)
{
ClipBackup := Clipboard
RunWait %pythonPath% "%cockpitPath%\evernote_helper.pyw" %headerLevel%
SendInput ^v
Sleep 100
Clipboard := ClipBackup
}

ChangeFormattingToHeader(headerLevel)
{
ClipBackup := Clipboard
RunWait %pythonPath% "%cockpitPath%\evernote_helper.pyw" %headerLevel%
SendInput ^v
Sleep 100
Clipboard := ClipBackup
}

^1::
SendEvernoteHeader("h1")
return

^2::
SendEvernoteHeader("h2")
return

^3::
SendEvernoteHeader("h3")
return

::opsy::opportunistically 
::nsy::necessarily 
::prio::priority 
::aes::aesthetic