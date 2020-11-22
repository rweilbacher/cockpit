import guizero
import datetime
import pyperclip
import sys

# November 22nd, 2020

daily_string ="""- #{0} #[[{1}]] Summary 
    - #[[summary-{0}]] #[[{1}]]
- #{0} #[[{1}]] Day rating 
    - #[[rating-{0}]] #[[{1}]]
- #{0} #[[{1}]] Important events 
    - #[[events-{0}]] #[[{1}]]
- #{0} #[[{1}]] Improvable 
    - How could I improve?
    - What could I have done better?
    - #[[better-{0}]] #[[{1}]]
- #{0} #[[{1}]] Bad 
    - What went badly that I had no influence on?
    - #[[bad-{0}]] #[[{1}]]
- #{0} #[[{1}]] Good
    - What did I do well today?
    - #[[good-{0}]] #[[{1}]]
- #{0} #[[{1}]] Best
    - What do I need to do if I want to be the best version of myself?
    - #[[best-{0}]] #[[{1}]]
- #{0} #[[{1}]] Progress
    - What progress did I make towards my goals today?
    - How am I improving?
    - Why is this important?
    - #[[progress-{0}]] #[[{1}]]
- #{0} #[[{1}]] Gratitude
    - What am I grateful for today?
    - #[[gratitude-{0}]] #[[{1}]]"""

weekdays = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

def copy_daily():
    today = datetime.date.today()
    week = "week" + str(today.isocalendar()[1])
    day = today.strftime("%Y-%m-%d") + " " + weekdays[today.weekday()]
    filled_template = daily_string.format(week, day)
    pyperclip.copy(filled_template)
    sys.exit()

app = guizero.App(title="Templates", width=200, height=100)
daily_button = guizero.PushButton(app, copy_daily, text="Daily review", align="left")
weekly_button = guizero.PushButton(app, copy_daily, text="Weekly review", align="right")
app.display()