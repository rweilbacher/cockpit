import HtmlClipboard
import sys

headerOne = """
<html>
<body>
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true"><b><span style="font-size: 24px;"><span style="color:rgb(0, 170, 59);">H1</span></span></b></div><div>text</div><!--EndFragment-->
</body>
</html>"""

headerTwo = """
<html>
<body>
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true"><b><span style="font-size: 20px;"><span style="color:rgb(0, 170, 59);">H2</span></span></b></div><div>text</div><!--EndFragment-->
</body>
</html>"""

headerThree = """
<html>
<body>
<!--StartFragment--><div data-pm-slice="1 1 []" data-en-clipboard="true"><span style="font-size: 18px;"><span style="color:rgb(0, 170, 59);">H3</span></span></div><div>text</div><!--EndFragment-->
</body>
</html>"""

#print(sys.argv)
#input()
headerDepth = sys.argv[1]
if headerDepth == "h1":
    HtmlClipboard.PutHtml(headerOne)
elif headerDepth == "h2":
    HtmlClipboard.PutHtml(headerTwo)
elif headerDepth == "h3":
    HtmlClipboard.PutHtml(headerThree)
else:
    print(sys.argv)
    input("Unrecognized argument!")