from instapaper import Instapaper as ipaper
import os
import datetime
import json


# Access to my personal secrets
with open("instapaper_credentials.json", "r") as file:
    credentials = json.loads(file.read())
    pass


# TODO Formatting issues:
    # Headings don't get recognized as such

EXPORT_FOLDER_NAME = "Export"
EXPORTED_FOLDER_NAME = "Exported"

EXPORT_PATH = "C:\\Users\\Roland\\Google Drive\\knowledge_base\\3 - Resources 📖\\"

MARKDOWN_HEADER_TEMPLATE = """**Tags: **

# {title}

**URL: ** {url}
**Author: **
**Starred: ** {starred}
**View date: ** {view_date}


"""


def sanitize_path(path):
    path = path.replace("?", "\uff1f")
    path = path.replace("/", "_")
    path = path.replace("\\", "_")
    path = path.replace(":", "-")
    path = path.replace("\"", "'")
    path = path.replace("|", "-")
    path = path.replace("*", "\uff0a")
    path = path.replace("<", "\uff1c")
    path = path.replace(">", "\uff1e")
    return path


def export_markdown_file(mark, path):
    with open(path, "w", encoding="utf-8") as file:
        iso_today = datetime.date.today().strftime("%Y-%m-%d")
        header = MARKDOWN_HEADER_TEMPLATE.format(title=mark.title, url=mark.url, view_date=iso_today,
                                                 starred=str(mark.starred))
        file.write(header)

        highlights = mark.get_highlights()
        highlights = json.loads(highlights)
        if len(highlights) == 0:
            print("No highlights found!")
        for highlight in highlights:
            file.write(">")
            # Keep quote going over a single empty line. Doesn't account for multiple empty lines
            text = highlight["text"].replace("\n\n", "\n>\n>")
            file.write(text)

            if highlight["note"] is not None:
                file.write("\n\n")
                file.write("*{}*".format(highlight["note"]))
            file.write("\n\n")


i = ipaper(credentials["client_id"], credentials["client_secret"])
i.login(credentials["username"], credentials["password"])
print("Logged in")

folders = i.folders()
export_folder_id = None
exported_folder_id = None
for folder in folders:
    if folder["title"] == EXPORT_FOLDER_NAME:
        print("Export folder ID: " + str(folder["folder_id"]))
        export_folder_id = folder["folder_id"]
    if folder["title"] == EXPORTED_FOLDER_NAME:
        print("Exported folder ID: " + str(folder["folder_id"]))
        exported_folder_id = folder["folder_id"]

if exported_folder_id is None:
    print("ERROR: Couldn't find folder for exported sources!")
    input()
    exit(-1)
if export_folder_id is None:
    print("ERROR: Couldn't find folder for sources that should be exported!")
    input()
    exit(-1)

marks = i.bookmarks(folder=export_folder_id, limit=100)

if len(marks) == 0:
    print("No new bookmarks found!")

for mark in marks:
    filename = sanitize_path(mark.title)
    print("Exporting \"" + mark.title + "\"")
    full_path = EXPORT_PATH + filename + ".md"
    if os.path.isfile(full_path):
        print("File \"" + full_path + "\" already exists!")
        continue
    export_markdown_file(mark, full_path)
    mark.move(exported_folder_id)
    print("Done with bookmark!")
print("Done!")
input("Press Enter to exit: ")
