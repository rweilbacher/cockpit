from system_hotkey import SystemHotkey
import pyperclip
from pynput.keyboard import Key, Controller
import time

keyboard = Controller()

def consumeHotkey(event, hotkey, args):
    time.sleep(0.1)
    string = args[0][0]
    print(string)
    keyboard.release(Key.alt)
    keyboard.type(string)


hk = SystemHotkey(consumer=consumeHotkey)

length = 0
with open('input.txt', 'r') as file:
    data = file.read().split("\n")
    for idx in range(0, len(data)):
        hk.register(('alt', str(idx+1)), data[idx])
        print("Alt + " + str(idx + 1) + ": " + data[idx])
    length = len(data)

print("\nHit Enter to exit")
input()

for idx in range(0, length):
    hk.unregister(('alt' + str(idx+1)))

# https://pynput.readthedocs.io/en/latest/keyboard.html