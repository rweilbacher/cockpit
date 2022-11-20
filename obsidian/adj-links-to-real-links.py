# I often have paragraphs like this in my daily notes:
# [[imaginal]] [[awareness]] [[love]] Something that connects to the imaginal, awareness and love.
# In my graph this will only show up as a link from the daily note to each of the concepts.
# But I want to have a real link between these files if they are mentioned next to each other.

# Problems:
# Do I only consider links right next to each other or in the same paragraph?
#   -> Only right next to each other for now
# In which file are the links persisted?
#   -> Naively build all permutations starting from the first in the list
# Where in the file are the links persisted? Start, end, custom block
#   -> Custom block at the beginning
# If the program is run again, how do I make sure that links aren't created again?
#   -> Always delete all links and recreate them
#   -> If this becomes too slow I might need a better solution
# If the file already contains text, how can I make SURE that nothing is ever lost?
#   -> Always write the links in the beginning of the file with a clear section end
#   -> Be very careful with the code that does this
#   -> Backup the vault beforehand
# Are all links that are next to each other considered or only concepts?
#   -> All links -> This might make prepending the links a bit more strange
# Do I only consider the daily files in the search?
#   -> Yes

import os
import re

inbox_path = "C:\\Users\\Roland\\Google Drive\\knowledge_base\\0 - Inbox\\"
vault_path = "C:\\Users\\Roland\\Google Drive\\knowledge_base\\"

# Structure
"""
Go through all daily notes (Verify filename structure, don't just go off of path)
    Find all links that are only separated by nothing or 1 to n whitespace characters excluding \n
    Build a graph of all of these nodes with an amount of links between the two on the edge
Write the results in the appropriate files 
"""

# Format
"""
imaginal.md
---
[[2022-10-02 Tue]] [[magic]]
[[2022-11-18 Fri]] [[awareness]] [[love]]
[[2022-11-18 Fri]] [[magic]]
--- end of links ---
Other text of the file
"""


# Vertices are identified by two strings. Order is irrelevant
# During the search process I need to search whether an edge between two vertices already exists


class Edge:
    edges_per_vertex = {}

    def __init__(self, vertices):
        self.vertices = vertices
        for vertex in self.vertices:
            if vertex in Edge.edges_per_vertex:
                Edge.edges_per_vertex[vertex] += 1
            else:
                Edge.edges_per_vertex[vertex] = 1
        self.weight = 1
        self.visited = False

    def inc_weight(self):
        self.weight += 1

    def visit(self):
        self.visited = True

    def __str__(self):
        string = ""
        for vertex in self.vertices:
            string += vertex + " "
        return string + "| " + str(self.weight)


# edges[frozenset(("imaginal", "awareness"))] = Edge(frozenset(("imaginal", "awareness")))


def find_links(edges, path):
    print(f"Constructing link graph from {path}")
    for item in os.listdir(path):
        if os.path.isfile(f"{path}\\{item}"):
            if re.search("[0-9]{4}-[0-9]{2}-[0-9]{2} ([a-z]|[A-Z]){3}.*", item) is not None:
                # File conforms to the daily name format
                analyze_file(edges, f"{path}\\{item}")
        else:
            find_links(edges, f"{path}\\{item}")
    return edges


def analyze_file(edges, path):
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
        result = re.finditer(
            "(\[\[[äöüÜÄÖa-zA-Z0-9-/ ]*\]\])(( | \t)*(\[\[[äöüÜÄÖa-zA-Z0-9-/ ]*\]\]))+",
            content)
    for obj in result:
        string = obj.string[obj.span()[0]:obj.span()[1]]
        split = re.split("[ \t]+\[", string)
        for i in range(0, len(split)):
            string = split[i]
            string = string.replace("[", "")
            string = string.replace("]", "")
            split[i] = string
        idx = 0
        while idx < len(split) - 1:
            for i in range(idx + 1, len(split)):
                key = frozenset((split[idx], split[i]))
                if key in edges:
                    edges[key].inc_weight()
                else:
                    edges[key] = Edge(key)
            idx += 1


def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


edges = find_links({}, inbox_path)
# This is inefficient, ugly and it turns out the data structure I chose is not helpful here but it works for now
# The problem is that I want to minimize the amount of file writes so I want to start from the vertex with the most edges and work my way down
# But my data structure makes that pretty suboptimal.
# Might not be a problem in the end but we will see.
for vertex, amount in sorted(Edge.edges_per_vertex.items(), key=lambda item: item[1], reverse=True):
    print(f"Writing to file {vertex}")
    links_string = ""
    for edge in edges.values():
        if vertex in edge.vertices and edge.visited is False:
            for inner_vertex in edge.vertices:
                if inner_vertex != vertex:
                    for i in range(0, edge.weight):
                        links_string += f"[[{inner_vertex}]] "
            edge.visit()
    if links_string == "":
        # No edges need to be visited for this vertex
        continue

    if "/" in vertex:
        # The link already contains the full path
        # Example: [[0 - Inbox/concepts/lists/principles]]
        vertex = str(vertex).replace("/", "\\")
        path = f"{vault_path}{vertex}.md"
    else:
        path = find_file(f"{vertex}.md", vault_path)
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    content = content.split("--- end of links ---\n")
    if len(content) == 1:
        old_content = content[0]
    else:
        old_content = content[1]
    new_content = f"{links_string}\n--- end of links ---\n{old_content}"
    with open(path, "w", encoding="utf-8") as file:
        file.write(new_content)
