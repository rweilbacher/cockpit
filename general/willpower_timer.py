# Reinforce your willpower by forcing yourself to hold down a key for X seconds until you are allowed to make a decision.

import guizero
import time
from pynput import keyboard
import subprocess

SECONDS_REQUIRED = "60"
startTime = 0

enableYouTube = False
# enableReddit = False
enableMoneySinks = False
enableHighDopamine = False
enableOther = False

actionExecuted = False

def onPress(key):
    global startTime
    if key == keyboard.Key.space and startTime == 0:
        startTime = int(time.time())


def onRelease(key):
    global startTime
    if key == keyboard.Key.space and startTime != 0:
        startTime = 0


def disable(event):
    # I have no idea why the key would change depending on where I run it from (It's the same OS)
    if event.key == "\r\n" or event.key == "\r" or event.key == "\n":
        event.widget.disable()


def updateLabel(text, timeRequired):
    global actionExecuted
    if startTime == 0:
        text.clear()
        text.append(timeRequired.value)
        return
    currTime = int(time.time())
    text.clear()
    newTime = int(timeRequired.value) - (currTime - startTime)
    text.append(newTime)
    if newTime == 0 and actionExecuted == False:
        executeActions()
        actionExecuted = True


def executeActions():
    global app
    print(f"Enable YouTube: {enableYouTube}")
    # print(f"Enable reddit: {enableReddit}")
    print(f"Enable money sinks: {enableMoneySinks}")
    print(f"Enable other: {enableOther}")
    print(f"Enable high dopamine: {enableHighDopamine}")
    if enableYouTube is False and enableMoneySinks is False and enableHighDopamine is False and enableHighDopamine is False:
        return
    command = ""
    if enableYouTube is True:
        command += "~/Scripts/unblock_youtube.sh;"
    # if enableReddit is True:
    #     command += "~/Scripts/unblock_reddit.sh;"
    if enableMoneySinks is True:
        command += "~/Scripts/unblock_money_sinks.sh;"
    if enableOther is True:
        command += "~/Scripts/unblock_other.sh;"
    if enableHighDopamine is True:
        command += "~/Scripts/unblock_high_dopamine.sh;"
    command += "pihole restartdns"

    ssh = subprocess.Popen(["ssh", "-i", "C:\\Users\\Roland\\Documents\\ssh\\raspberrypi_ecdsa", "pi@192.168.2.154", command])
    ssh.wait()

    flushDns = subprocess.Popen(["ipconfig", "/flushdns"], shell=True)
    flushDns.wait()
    # This doesn't show up but at least it makes a noise
    app.info("Done!", "All actions have been completed!")
    app.display()

def updateActions(checkBox):
    global enableYouTube
    # global enableReddit
    global enableMoneySinks
    global enableHighDopamine
    global enableOther
    if checkBox.text == "Enable YouTube":
        enableYouTube = bool(checkBox.value)
    # elif checkBox.text == "Enable reddit":
    #     enableReddit = bool(checkBox.value)
    elif checkBox.text == "Enable money sinks":
        enableMoneySinks = bool(checkBox.value)
    elif checkBox.text == "Enable other":
        enableOther = bool(checkBox.value)
    elif checkBox.text == "Enable dopamine sites":
        enableHighDopamine = bool(checkBox.value)


listener = keyboard.Listener(on_press=onPress, on_release=onRelease)
listener.start()

gridHeight = 0
app = guizero.App(title="Question Timer", width=380, height=130, layout="grid")
youtubeCheckbox = guizero.CheckBox(app, text="Enable YouTube", grid=[0, gridHeight], align="left")
youtubeCheckbox.update_command(updateActions, [youtubeCheckbox])
# redditCheckbox = guizero.CheckBox(app, text="Enable reddit", grid=[1, gridHeight], align="left")
# redditCheckbox.update_command(updateActions, [redditCheckbox])
# gridHeight += 1
moneySinksCheckbox = guizero.CheckBox(app, text="Enable money sinks", grid=[1, gridHeight], align="left")
moneySinksCheckbox.update_command(updateActions, [moneySinksCheckbox])
gridHeight += 1
otherCheckbox = guizero.CheckBox(app, text="Enable other", grid=[0, gridHeight], align="left")
otherCheckbox.update_command(updateActions, [otherCheckbox])
highDopamineCheckbox = guizero.CheckBox(app, text="Enable dopamine sites", grid=[1, gridHeight], align="left")
highDopamineCheckbox.update_command(updateActions, [highDopamineCheckbox])
gridHeight += 1
timeRequiredLabel = guizero.Text(app, text="Time Required", grid=[0, gridHeight], align="left")
timeRequired = guizero.TextBox(app, text=SECONDS_REQUIRED, grid=[1, gridHeight], width=3, align="left")
gridHeight += 1
questionLabel = guizero.Text(app, text="Reason", grid=[0, gridHeight], align="left")
question = guizero.TextBox(app, text="", grid=[1, gridHeight], width=40, align="left")
gridHeight += 1
timeRemainingLabel = guizero.Text(app, text=SECONDS_REQUIRED, grid=[1, gridHeight])
gridHeight += 1

question.focus()
question.when_key_pressed = disable

timeRemainingLabel.repeat(100, updateLabel, [timeRemainingLabel, timeRequired])
app.display()

listener.stop()
