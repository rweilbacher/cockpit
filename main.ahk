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
; $ prefix disables activation of the hotkey by its own Send commands

; global variable to enable and disable custom Evernote hotkeys, since they might clash with other applications
global enableEvernote = false
; TODO Replace with a more flexible approach to start python
global pythonPath = "C:\Users\Roland\AppData\Local\Programs\Python\Python37\pythonw.exe"

global DE_KEY_LAYOUT = 0x4070407
global EN_KEY_LAYOUT = 0x4090409

; Hotkeys that make small changes and reloads much faster
+F5::Edit ; Shift-F5 launches the current AutoHotkey script in preferred editor, else Notepad
^F5::Reload ; Ctrl-F5 reloads the current AutoHotKey script after any edits.

; --- General hotkeys ---

; Send the current date in ISO format
!2::
FormatTime, CurrentDateTime,, yyyy-MM-dd
SendInput %CurrentDateTime%
return


; Start the templates python script, which is a small GUI for selecting templates to load into the Clipboard
!F2::
RunWait %pythonPath% ".\templates.py"
return

!a::

return

; --- Evernote Utils ---

changeFormattingToEvernoteHeader(headerLevel)
{
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
}

toggleEverNoteTextColor()
{
ClipBackup := Clipboard
SendInput ^c
Sleep 50
RunWait %pythonPath% ".\evernote_textcolor.py"
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
changeFormattingToEvernoteHeader("h0")
return

$^1::
if (enableEvernote = false) {
    Send, ^1
    return
}
changeFormattingToEvernoteHeader("h1")
return

$^2::
if (enableEvernote = false) {
    Send, ^2
    return
}
changeFormattingToEvernoteHeader("h2")
return

$^3::
if (enableEvernote = false) {
    Send, ^3
    return
}
changeFormattingToEvernoteHeader("h3")
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