import win32clipboard
import re

win32clipboard.OpenClipboard()
text = win32clipboard.GetClipboardData()
formatted = re.sub("(\r\n|^)[0-9:]*\r\n", " ", text)
win32clipboard.EmptyClipboard()
win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, formatted)
win32clipboard.CloseClipboard()

