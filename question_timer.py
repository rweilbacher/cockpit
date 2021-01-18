# Reinforce your willpower by forcing yourself to hold down a key for X seconds until you are allowed to make a decision.

import guizero
import time
from pynput import keyboard

SECONDS_REQUIRED = 10
startTime = 0

def onPress(key):
    global startTime
    if key == keyboard.Key.space and startTime == 0:
        startTime = int(time.time())


def onRelease(key):
    global startTime
    if key == keyboard.Key.space and startTime != 0:
        startTime = 0


def updateLabel(text, timeRequired):
    if startTime == 0:
        text.clear()
        text.append(timeRequired.value)
        return
    currTime = int(time.time())
    text.clear()
    text.append(int(timeRequired.value) - (currTime - startTime))


listener = keyboard.Listener(on_press=onPress, on_release=onRelease)
listener.start()

app = guizero.App(title="Question Timer", width=360, height=80, layout="grid")
timeRequiredLabel = guizero.Text(app, text="Time Required", grid=[0, 0])
timeRequired = guizero.TextBox(app, text="30", grid=[1, 0], width=3, align="left")
questionLabel = guizero.Text(app, text="Question", grid=[0, 1])
question = guizero.TextBox(app, text="", grid=[1, 1], width=40)
timeRemainingLabel = guizero.Text(app, text=SECONDS_REQUIRED, grid=[1, 3])

timeRemainingLabel.repeat(100, updateLabel, [timeRemainingLabel, timeRequired])
app.display()

listener.stop()
