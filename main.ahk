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

global alternative_umlauts = false

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
;+F5::Edit ; Shift-F5 launches the current AutoHotkey script in preferred editor, else Notepad
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
    if (ErrorLevel < 0) {
        MsgBox, python script %path% encountered an error!
    }
    else {
        return ErrorLevel
    }
}

runPythonModule(module, console, args*) {
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
    RunWait %pythonExec% -m %module% %argsString%,, UseErrorLevel
    MsgBox, %ErrorLevel%
    if (ErrorLevel < 0) {
        MsgBox, python script %module% encountered an error!
    }
    else {
        return ErrorLevel
    }
}

readResultFile() {
    if (! FileExist(".\tmp_result")) {
        TrayTip, Error, Result not found, 3
        return
    }
    FileRead, result, .\tmp_result
    FileDelete, .\tmp_result
    return result
}

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

; --- General hotkeys ---

; Send the current date in ISO format
!2::
FormatTime, CurrentDateTime,, yyyy-MM-dd
SendInput %CurrentDateTime%
return

; Start the templates python script, which is a small GUI for selecting templates to load into the Clipboard
!F2::
runPythonScript(".\general\templates.py", false)
return

!F3::
Hotkey, !2, Off
runPythonScript(".\general\multi_paster.py", true)
Hotkey, !2, On
return

!F10::
runPythonScript(".\pihole\pihole_blocker.py", false)
return

!F11::
runPythonScript(".\general\willpower_timer.py", false)
return

!F5::
runPythonScript(".\general\daily_template.py", false)
return

!+F5::
runPythonScript(".\general\daily_template.py", false, 1)
return

!q::
if (alternative_umlauts = true) {
    global alternative_umlauts = false
	TrayTip, Umlaut switch, off
}
else {
    global alternative_umlauts = true
	TrayTip, Umlaut switch, on
}
return

!F9::
runPythonModule("data_transfer.instapaper_export", true)
return

!g::
ctmp := Clipboard ; what's currently on the clipboard
SendInput ^c ; copy to clipboard
ClipWait, 2
runPythonScript(".\general\text_stats.py", false)
result := readResultFile()
TrayTip, Text statistics, %result%, 16
Clipboard := ctmp
return

moveLine(direction) {
    sleep_time := 20
    Send, {End}
    Sleep, %sleep_time%
    Send, {SHIFT}+{Home}
    Sleep, %sleep_time%
    ClipBackup := Clipboard
    Send, ^x
    ClipWait, 2 ; wait for the clipboard to change
    Sleep, %sleep_time%
    Send, {Backspace}
    Sleep, %sleep_time%
    Send, {%direction%}
    Sleep, %sleep_time%
    Send, {End}
    Sleep, %sleep_time%
    Send {Enter}
    Sleep, %sleep_time%
    SendInput, ^v
    Sleep, %sleep_time%
    Clipboard := ClipBackup
}

; As expected these hotkeys were too unstable to be usable
;^+Down::
;moveLine("Down")
;return

;^+Up::
;moveLine("Up")
;return

; --- Keyboard layout hotkeys ---

; Play sound and display tray icon on keyboard layout switch
global altShiftDownTime = 0
~!LShift::
altShiftDownTime := A_NowUTC
; No idea why but you need to wait here
KeyWait, LShift
return
~!LShift Up::
elapsed := A_NowUTC - altShiftDownTime
if (elapsed >= 2) {
    ; Shift + Alt was pressed for longer than 1 sec and I didn't intend to switch language
    return
}
locale := getInputLocaleId()
if (locale = DE_KEY_LAYOUT) {
    SoundPlay, .\de.wav
    TrayTip, DEU, DEU,
}
else if (locale = EN_KEY_LAYOUT) {
    SoundPlay, .\en.wav
    TrayTip, ENG, ENG
}
return

; Permanent rebind for y & z on German keyboard

$y::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, y
    return
}
Send, z
return

$z::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, z
    return
}
Send, y
return

; -- More convenient hotkeys for []{};:'" on the German keyboard layout--

; - ü -

$#vkBA::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, {LWin}{vkBA}
    return
}
Send, [
return

$+#vkBA::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, {LWin}{vkBA}
    return
}
Send, {{}
return

; - + -

$#SC01B::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, {LWin}{SC01B}
    return
}
Send, ]
return

$+#SC01B::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, {LShift}{LWin}{SC01B}
    return
}
Send, {}}
return

; - ö -

$#vkC0::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, {LWin}{vkC0}
    return
}
Send, `;
return

$+#vkC0::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, {LShift}{LWin}{vkC0}
    return
}
Send, :
return

; - ä -

$#vkDE::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, {LWin}{vkDE}
    return
}
Send, '
return

$+#vkDE::
locale := getInputLocaleId()
if (locale = EN_KEY_LAYOUT) {
    Send, {LShift}{LWin}{vkDE}
    return
}
Send, "
return

; --- Markdown Utils ---

#!c:: ; win+alt+c
ctmp := Clipboard ; what's currently on the clipboard
Clipboard := ""
SendInput ^c ; copy to clipboard
ClipWait, 2 ; wait for the clipboard to change
Clipboard := "[" . Clipboard . "](" . ctmp . ")"
Sleep 30
SendInput ^v
Sleep 30
Clipboard := ctmp
Return

; --- Paste formatting ---

; Replaces all newlines in the Clipboard with spaces
^!v::
StringReplace, Clipboard, Clipboard, `r, , A
ClipWait, 2
StringReplace, Clipboard, Clipboard, `n, %A_Space%, A
ClipWait, 2
SendInput ^v
return


; --- Evernote Utils ---

changeFormattingToEvernoteHeader(headerLevel)
{
Send, {SHIFT}+{Home}
Sleep 30
ClipBackup := Clipboard
SendInput ^c
Sleep 30
runPythonScript(".\evernote\evernote_header.pyw", false, headerLevel)
SendInput ^v
Sleep 30
Clipboard := ClipBackup
}

toggleEverNoteTextColor()
{
ClipBackup := Clipboard
SendInput ^c
Sleep 50
runPythonScript(".\evernote\evernote_textcolor.py", false)
SendInput ^v
Sleep 50
Clipboard := ClipBackup
}

!F12::
if (enableEvernote = true) {
    global enableEvernote = false
	TrayTip, Evernote Hotkeys, off
}
else {
    global enableEvernote = true
	TrayTip, Evernote Hotkeys, on
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

; Alternative Mouse scroll to reduce strain on right hand
!s::
Click WheelDown
return		

; Alternative Mouse scroll to reduce strain on right hand
!w::
Click WheelUp
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

; Alternative Backspace to reduce strain on right hand
$^::
inputLocaleId := getInputLocaleId()
if (inputLocaleId = DE_KEY_LAYOUT) {
    Send, {Backspace}
}
else if (inputLocaleId = EN_KEY_LAYOUT) {
    Send, ^
}
return
														
; --- Word expansions ---

::opsy::opportunistically 
::nsy::necessarily 
::prio::priority 
::aes::aesthetic
::delib::deliberately
::conti::continuous
::conty::continuously
::consc::consciousness
::conscy::consciously
::dont::don't
::doesnt::doesn't
::cant::can't
::wont::won't
::havent::haven't
::couldnt::couldn't
::arent::aren't
::wouldnt::wouldn't
::wasnt::wasn't
::didnt::didn't
::imt::important
::assu::assumption
::urose::purpose
::andre::andré
::bjoern::björn

; TODO Disable hotkeys instead of checking
; TODO Or go the other way. Make symbols easier to use on qwertz
replaceUmlaut(umlaut, alternativeEncoding) {
    inputLocaleId := getInputLocaleId()
    if (inputLocaleId = DE_KEY_LAYOUT) {
        Send, %alternativeEncoding%
    }
    else if (inputLocaleId = EN_KEY_LAYOUT) {
        if (alternative_umlauts = true) {
            Send, %umlaut%
        }
        else {
            Send, %alternativeEncoding%
        }
    }
}

;:?*:ue::
;replaceUmlaut("ü", "ue")
;return

;:?*:oe::
;replaceUmlaut("ö", "oe")
;return

;:?*:ae::
;replaceUmlaut("ä", "ae")
;return

;:?*:sss::
;replaceUmlaut("ß", "sss")
;return

