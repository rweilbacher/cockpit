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
SendInput ^+{Left}
Sleep 30
ClipBackup := Clipboard
SendInput ^c
Sleep 30
RunWait %pythonPath% "%cockpitPath%\evernote_header.pyw" %headerLevel%
SendInput ^v
Sleep 30
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

^0::
ChangeFormattingToEvernoteHeader("h0")
return

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

`::
Send, {Backspace}
return

!s::
Click WheelDown
return		

!w::
Click WheelUp
return	

!q::
Send, {Enter}
return
														

::opsy::opportunistically 
::nsy::necessarily 
::prio::priority 
::aes::aesthetic
::delib::deliberately
::consc::consciousness
::conscy::consciously
::dont::don't
::cant::can't
::wont::won't
::didnt::didn't
::imt::important
::assu::assumption
::urose::purpose