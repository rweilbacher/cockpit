import os

path = "C:\\Users\\Roland\\Google Drive\\knowledge_base\\0 - Inbox"


def find_principles(path):
    principles = []
    for item in os.listdir(path):
        if os.path.isfile(f"{path}\\{item}"):
            principles = principles + analyze_file(item.replace(".md", ""), f"{path}\\{item}")
        else:
            principles = principles + find_principles(f"{path}\\{item}")
    return principles


def analyze_file(source, path):
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    idx = content.find("[[principles]]")
    principles = []
    while idx < len(content) and idx != -1:
        principle = ""
        newline_counter = 0
        while idx < len(content) and newline_counter < 2:
            if content[idx] == "\n":
                newline_counter += 1
            else:
                newline_counter = 0
            principle += content[idx]
            idx += 1
        principle = principle.replace("[[principles]]", f"[[{source}]]")
        principles.append(principle.replace("\n\n", ""))
        idx = content.find("[[principles]]", idx)
    return principles


principles = find_principles(path)
with open("result.md", "w", encoding="utf-8") as file:
    for principle in principles:
        file.write(f"{principle}\n\n")


