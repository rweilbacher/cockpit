# This script takes the current text from the clipboard
# puts some HTML with style information around it and then puts it back into the HTML clipboard.
# Which style information gets put around the text depends on a command line argument

import HtmlClipboard
import sys
import win32clipboard

headerZero = """
<html>
<body>
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true"><span style="font-size: 16px;">{}</span></div><!--EndFragment-->
</body>
</html>
"""

headerOne = """
<html>
<body>
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true"><b><span style="font-size: 24px;"><span style="color:rgb(0, 170, 59);">{}</span></span></b></div><!--EndFragment-->
</body>
</html>"""

headerTwo = """
<html>
<body>
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true"><b><span style="font-size: 20px;"><span style="color:rgb(0, 170, 59);">{}</span></span></b></div><!--EndFragment-->
</body>
</html>"""

headerThree = """
<html>
<body>
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true"><span style="font-size: 18px;"><span style="color:rgb(0, 170, 59);">{}</span></span></div><!--EndFragment-->
</body>
</html>"""


headerDepth = sys.argv[1]
win32clipboard.OpenClipboard()
text = win32clipboard.GetClipboardData()
win32clipboard.CloseClipboard()
if headerDepth == "h0":
    HtmlClipboard.PutHtml(headerZero.format(text))
elif headerDepth == "h1":
    HtmlClipboard.PutHtml(headerOne.format(text))
elif headerDepth == "h2":
    HtmlClipboard.PutHtml(headerTwo.format(text))
elif headerDepth == "h3":
    HtmlClipboard.PutHtml(headerThree.format(text))
else:
    print(sys.argv)
    input("Unrecognized argument!")