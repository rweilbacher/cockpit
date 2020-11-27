# Toggles the text color of the clipboard between red and black

import HtmlClipboard
import win32clipboard

redText = """
<html>
<body>
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true"><span style="color:rgb(255, 0, 42);">{}</span></div><!--EndFragment-->
</body>
</html>
"""

blackText = """
<html>
<body>  
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true">{}</div><!--EndFragment-->
</body>
</html>
"""

win32clipboard.OpenClipboard()
text = win32clipboard.GetClipboardData()
win32clipboard.CloseClipboard()
html = HtmlClipboard.GetHtml()
if "rgb(255, 0, 42)" in html:
    HtmlClipboard.PutHtml(blackText.format(text))
else:
    HtmlClipboard.PutHtml(redText.format(text))