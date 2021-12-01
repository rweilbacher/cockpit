import json
import sys
import datetime
import os

EXPORT_PATH = "C:\\Users\\Roland\\Google Drive\\knowledge_base\\3 - Resources\\"

MARKDOWN_HEADER_TEMPLATE = """**Tags: **

# {title}

**Author: **
**Starred: **
**Creation Date: ** {date}

"""

MARKER_TAGS = ["Chapter"]


def format_clip(text, marker_tags):
    formatted_text = ""
    if "Chapter" in marker_tags:
        formatted_text += "# "
    else:
        formatted_text += "> "
    formatted_text += text + "\n\n"
    return formatted_text


file = open("./clippit_backup.json", encoding="utf-8")
data = json.load(file)
file.close()

marker_tags_dict = {}
books = []
for tag_id in data["tags"]:
    tag = data["tags"][tag_id]["text"]
    if tag not in MARKER_TAGS:
        books.append(tag)
    else:
        marker_tags_dict[int(tag_id)] = data["tags"][tag_id]["text"]
if len(books) > 1:
    print("Only one book can be exported at a time!")
    sys.exit(-1)

print(books[0])
clips = data["clips"]
clips.reverse()
previous_id = -1
output = ""
for clip in clips:
    if clip["id"] <= previous_id:
        print("ID error!")
        sys.exit(-2)

    marker_tags = []
    for tag_id in clip["tags"]:
        if tag_id in marker_tags_dict.keys():
            marker_tags.append(marker_tags_dict[tag_id])

    output += format_clip(clip["text"], marker_tags)

filename = books[0]
full_path = EXPORT_PATH + filename + ".md"
if os.path.isfile(full_path):
    print("File \"" + full_path + "\" already exists!")
    sys.exit(-3)
with open(full_path, "w", encoding="utf-8") as file:
    iso_today = datetime.date.today().strftime("%Y-%m-%d")
    header = MARKDOWN_HEADER_TEMPLATE.format(title=filename, date=iso_today)
    file.write(header)
    file.write(output)
