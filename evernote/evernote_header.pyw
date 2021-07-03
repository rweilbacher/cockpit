# This script takes the current text from the clipboard
# puts some HTML with style information around it and then puts it back into the HTML clipboard.
# Which style information gets put around the text depends on the first command line argument

# TODO Find out if I can generate a ToC (Maybe I can add hidden HTML attributes?)

import libs.HtmlClipboard as HtmlClipboard
import sys
import win32clipboard

textFontSize = 16
textColor = "0, 0, 0"

headerFontSizes = [24, 20, 18]
headerColors = ["0, 170, 59",
                "0, 170, 59",
                "0, 170, 59"]
boldStates = [True, True, False]
italicStates = [False, False, False]
MAX_HEADER_DEPTH = 3

bodyTemplate = """
<html>
<body>
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true"><span style="font-size: {0}px;"><span style="color:rgb({1});">{2}</span></span></div><!--EndFragment-->
</body>
</html>
"""

headerTemplateStart = """
<html>
<body>
<!--StartFragment-->
<div data-pm-slice="1 1 []" data-en-clipboard="true">{openTags}<span style="font-size: {fontSize}px;"><span style="color:rgb({textColor});">{text}</span></span>{closeTags}
</div>"""

headerTemplateEnd = """<div><span style="font-size: {0}px;"><span style="color:rgb({1});"></span></span></div>
<!--EndFragment-->
</body>
</html>
"""

def createHeaderHtml(text, fontSize, textColor, bold, italics):
    openTags = ""
    closeTags = ""
    if bold is True:
        openTags += "<b>"
        closeTags += "</b>"
    if italics is True:
        openTags += "<i>"
        closeTags += "</i>"
    html = headerTemplateStart.format(openTags=openTags, fontSize=fontSize, textColor=textColor, text=text, closeTags=closeTags)
    # Reset font size and text color to that of the normal body text
    html += headerTemplateEnd.format(textFontSize, textColor)
    return html


win32clipboard.OpenClipboard()
try:
    text = win32clipboard.GetClipboardData()
except TypeError:
    # Clip board data is not available
    text = ""
win32clipboard.CloseClipboard()
if len(sys.argv) < 2:
    input("Missing command line parameter! Pass a number between 0 and {} for header depth".format(MAX_HEADER_DEPTH))
    sys.exit(-1)
headerDepth = sys.argv[1]
try:
    headerDepth = int(headerDepth)
except ValueError:
    print(sys.argv)
    input("Unrecognized argument! Pass a number between 0 and {}".format(MAX_HEADER_DEPTH))
    sys.exit(-1)

if headerDepth == 0:
    html = bodyTemplate.format(textFontSize, textColor, text)
    HtmlClipboard.PutHtml(html)
elif headerDepth > MAX_HEADER_DEPTH or headerDepth < 0:
    input("Header depth {0} not within range 0 to {1}!".format(headerDepth, MAX_HEADER_DEPTH))
    sys.exit(-1)
else:
    idx = headerDepth - 1
    html = createHeaderHtml(text, headerFontSizes[idx], headerColors[idx], boldStates[idx], italicStates[idx])
    HtmlClipboard.PutHtml(html)