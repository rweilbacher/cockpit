import guizero
import subprocess

disableYouTube = True
disableReddit = True
disableHighDopamine = True
disableOther = True


def executeActions():
    if disableYouTube is False and disableReddit is False and disableHighDopamine is False and disableOther is False:
        return
    command = ""
    if disableYouTube is True:
        command += "~/Scripts/block_youtube.sh;"
    if disableReddit is True:
        command += "~/Scripts/block_reddit.sh;"
    if disableHighDopamine is True:
        command += "~/Scripts/block_other.sh;"
    if disableOther is True:
        command += "~/Scripts/block_high_dopamine.sh;"
    command += "pihole restartdns"

    ssh = subprocess.Popen(["ssh", "-i", "C:\\Users\\Roland\\Documents\\ssh\\raspberrypi_ecdsa", "pi@192.168.2.154", command])
    ssh.wait()

    flushDns = subprocess.Popen(["ipconfig", "/flushdns"], shell=True)
    flushDns.wait()
    app.info("Done!", "All actions have been completed!")
    app.display()


def updateActions(checkBox):
    global disableYouTube
    global disableReddit
    global disableHighDopamine
    global disableOther
    if checkBox.text == "Block YouTube":
        disableYouTube = bool(checkBox.value)
    elif checkBox.text == "Block reddit":
        disableReddit = bool(checkBox.value)
    elif checkBox.text == "Block other":
        disableHighDopamine = bool(checkBox.value)
    elif checkBox.text == "Block dopamine sites":
        disableOther = bool(checkBox.value)


gridHeight = 0
app = guizero.App(title="pihole blocker", width=280, height=100, layout="grid")
youtubeCheckbox = guizero.CheckBox(app, text="Block YouTube", grid=[0, gridHeight], align="left")
youtubeCheckbox.update_command(updateActions, [youtubeCheckbox])
youtubeCheckbox.toggle()
redditCheckbox = guizero.CheckBox(app, text="Block reddit", grid=[1, gridHeight], align="left")
redditCheckbox.update_command(updateActions, [redditCheckbox])
redditCheckbox.toggle()
gridHeight += 1
otherCheckbox = guizero.CheckBox(app, text="Block other", grid=[0, gridHeight], align="left", )
otherCheckbox.update_command(updateActions, [otherCheckbox])
otherCheckbox.toggle()
highDopamineCheckbox = guizero.CheckBox(app, text="Block dopamine sites", grid=[1, gridHeight], align="left")
highDopamineCheckbox.update_command(updateActions, [highDopamineCheckbox])
highDopamineCheckbox.toggle()
gridHeight += 1
button = guizero.PushButton(app, text="Execute", grid=[0, gridHeight])
button.update_command(executeActions)


app.display()
