from xml.etree.ElementTree import Element, SubElement, Comment, tostring

APP_VER = "8.0.3.0"
FILE_FORMAT = "12"
FILE_VERSION = "1"
TEXT_COLOR = "0"
TEXT_WEB_COLOR = "#000000"
COMMENTS_TYPE = "PLAIN_TEXT"
CREATED_BY = "Python"
PERCENT_DONE = "0"

TDL_HEADER = '<?xml version="1.0" encoding="utf-8"?>\n'


def addStaticTaskAttributes(taskXml):
    taskXml.set("TEXTCOLOR", TEXT_COLOR)
    taskXml.set("TEXTWEBCOLOR", TEXT_WEB_COLOR)
    taskXml.set("LASTMODBY", CREATED_BY)
    taskXml.set("COMMENTSTYPE", COMMENTS_TYPE)
    taskXml.set("CREATEDBY", CREATED_BY)


class TaskList:
    def __init__(self, projectName):
        self.projectName = projectName
        self.nextId = 1
        self.children = []
        self.root = Element("TODOLIST")
        self.root.set("PROJECTNAME", projectName)
        self.root.set("FILEVERSION", FILE_VERSION)
        self.root.set("APPVER", APP_VER)
        self.root.set("FILEFORMAT", FILE_FORMAT)

        SubElement(self.root, "STATUS")
        SubElement(self.root, "ALLOCATEDBY")
        SubElement(self.root, "VERSION")

    def createSubTask(self, title, priority=5):
        taskXml = SubElement(self.root, "TASK")
        taskXml.set("ID", str(self.nextId))
        self.nextId += 1
        taskXml.set("TITLE", title)
        taskXml.set("PRIORITY", str(priority))

        pos = len(self.children)
        taskXml.set("POS", str(pos))
        taskXml.set("POSSTRING", str(pos + 1))

        addStaticTaskAttributes(taskXml)

        task = Task(self, None, title, taskXml, len(self.children))
        self.children.append(task)
        return task

    def getNextId(self):
        self.nextId += 1
        currNextId = self.nextId
        return currNextId

    def toString(self):
        return TDL_HEADER + tostring(self.root).decode("utf-8")


class Task:
    def __init__(self, taskList, parent, title, xml, pos):
        self.taskList = taskList
        self.parent = parent
        self.title = title
        self.xml = xml
        self.pos = pos
        self.children = []

    def __str__(self):
        return self.title

    def createSubTask(self, title, priority=5):
        subTaskXml = SubElement(self.xml, "TASK")
        subTaskXml.set("ID", str(self.taskList.getNextId()))
        subTaskXml.set("TITLE", title)
        subTaskXml.set("PRIORITY", str(priority))

        subTaskXml.set("POS", str(len(self.children)))

        posString = str(self.pos + 1)
        parent = self.parent
        while parent is not None:
            posString = str(parent.pos + 1) + "." + posString
            parent = parent.parent
        posString = posString + '.' + str(len(self.children) + 1)
        subTaskXml.set("POSSTRING", posString)

        addStaticTaskAttributes(subTaskXml)

        subTask = Task(self.taskList, self, title, subTaskXml, len(self.children))
        self.children.append(subTask)
        return subTask


# with open("out.tdl", "w") as tdlFile:
#     taskList = TaskList("Test")
#     task = taskList.createSubTask("Task1", priority=9)
#     task2 = task.createSubTask("Task2")
#     task2.createSubTask("Task3")
#     task.createSubTask("Task4")
#     tdlFile.write(taskList.toString())


