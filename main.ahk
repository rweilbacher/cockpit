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

global enableEvernote = true
global pythonPath = "C:\Users\Roland\AppData\Local\Programs\Python\Python37\pythonw.exe"

+F5::Edit ; Shift-F5 launches the current AutoHotkey script in preferred editor, else Notepad 

^F5::Reload ; Ctrl-F5 reloads the current AutoHotKey script after any edits.

!2::
FormatTime, CurrentDateTime,, yyyy-MM-dd
SendInput %CurrentDateTime%
return

changeFormattingToEvernoteHeader(headerLevel)
{
if (enableEvernote = false) {
    return false
}
;TODO select the entire line with SendPlay and Home
Send, ^+{Left}
Sleep 30
ClipBackup := Clipboard
SendInput ^c
Sleep 30
RunWait %pythonPath% ".\evernote_header.pyw" %headerLevel%
SendInput ^v
Sleep 30
Clipboard := ClipBackup
return true
}

toggleEverNoteTextColor()
{
if (enableEvernote = false) {
    return false
}
ClipBackup := Clipboard
SendInput ^c
Sleep 50
RunWait %pythonPath% ".\evernote_textcolor.py"
SendInput ^v
Sleep 50
Clipboard := ClipBackup
return true
}

isLangEn()
{
DE = 0x4070407
EN = 0x4090409
SetFormat, Integer, H
  WinGet, WinID,, A
  ThreadID:=DllCall("GetWindowThreadProcessId", "UInt", WinID, "UInt", 0)
  InputLocaleID:=DllCall("GetKeyboardLayout", "UInt", ThreadID, "UInt")
  if (EN = InputLocaleID) {
    return true
  } else {
    return false
  }
}

!F12::
if (enableEvernote = true) {
    global enableEvernote = false
}
else {
    global enableEvernote = true
}
return

$^0::
success := changeFormattingToEvernoteHeader("h0")
if (success = false) {
    Send, ^0
}
return

$^1::
success := changeFormattingToEvernoteHeader("h1")
if (success = false) {
    Send, ^1
}
return

$^2::
success := changeFormattingToEvernoteHeader("h2")
if (success = false) {
    Send, ^2
}
return

$^3::
success := changeFormattingToEvernoteHeader("h3")
if (success = false) {
    Send, ^3
}
return

$^g::
success := toggleEverNoteTextColor()
if (success = false) {
    Send, ^g
}
return

$`::
if (isLangEn() = true) {
    Send, {Backspace}
}
else {
    Send, ö
}
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

!F2::
RunWait %pythonPath% ".\templates.py"
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