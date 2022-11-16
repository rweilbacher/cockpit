import os
import jsonpickle
import re

# TODO: Include the whole vault

path = "C:\\Users\\Roland\\Google Drive\\knowledge_base\\0 - Inbox"


class Principle:
    def __init__(self, source, links, text):
        self.source = source
        self.text = text
        self.links = links
        self.last_shown = ""

    def links_to_str(self):
        result = ""
        for link in self.links:
            result += link + " "
        return result[:-1]

    def __str__(self):
        if len(self.links) == 0:
            return f"{self.source} {self.text}"
        else:
            return f"{self.source} {self.links_to_str()} {self.text}"


def find_principles(path):
    principles = []
    for item in os.listdir(path):
        if item == "principles.md":
            # Skip the principles file itself
            continue
        elif os.path.isfile(f"{path}\\{item}"):
            principles = principles + analyze_file(item.replace(".md", ""), f"{path}\\{item}")
        else:
            principles = principles + find_principles(f"{path}\\{item}")
    return principles


# TODO Separate scenarios like below into multiple principles
"""
- [[principles]] Invite calmness/relaxation/dropping resistance. Intend to release tension. Intend to unclench your soul
- [[principles]] Be fully aware and awake to the experience of feeling unmotivated. Accept it and intend to let go of wanting it to be different
- [[principles]] Be fully aware of your sense of motivation, enjoyment and wanting of the soul. "Am I doing this to distract myself from my existence or am I enjoying it on some level?". "If the things I *need* (or I imagine I need) to do are not on the menu of my soul, what is?"
- [[principles]] Don't fall into imaginary commitment traps. Just because I started to watch a YouTube video doesn't mean I need to finish it if I don't enjoy it. Just because I started a match doesn't mean I need to finish it. Just because I have been scrolling endless feeds for 15min doesn't mean I need to continue doing it. You can get fed up with something
- [[principles]] Let go of things you think you *need* to do. 
"""

def analyze_file(source, path):
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    idx = content.find("[[principles]]")
    principles = []
    while idx < len(content) and idx != -1:
        text = ""
        newline_counter = 0
        while idx < len(content) and newline_counter < 2:
            if content[idx] == "\n":
                newline_counter += 1
            else:
                newline_counter = 0
            text += content[idx]
            idx += 1

        text = text.replace("[[principles]]", "")
        text = text.replace("\n\n", "")

        # Filter out tags like: #authors/dean-dingus and links like: [[love]]
        links = []
        splits = re.split("(#[äöüÜÖÄa-zA-Z0-9-/]*|\[\[[äöüÜÄÖa-zA-Z0-9-/]*\]\])", text)
        text = ""
        for split in splits:
            if split.startswith("[[") or split.startswith("#"):
                links.append(split)
            else:
                text += split

        text = re.sub(" +", " ", text)
        text = text.lstrip()
        principles.append(Principle(source, links, text))

        idx = content.find("[[principles]]", idx)
    return principles


principles = find_principles(path)
with open("all_principles.md", "w", encoding="utf-8") as markdown_file, open("all_principles.json", "w", encoding="utf-8") as json_file:
    print(f"Number of principles: {len(principles)}")
    for principle in principles:
        markdown_file.write(f"{principle}\n\n")
    # json_file.write(jsonpickle.encode(principles, make_refs=False, unpicklable=False, indent=1))
    json_file.write(jsonpickle.encode(principles, indent=1))

