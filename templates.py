import guizero
import datetime
import pyperclip
import sys

# region Roam Research templates

# The purpose of the review templates is to be able to aggregate the information of each day or week automatically.
# Reviewing a week is much easier when you have the information from every day,
# neatly in one place without having to jump around.
# This is achieved by combining Roam links with queries.

# Template for daily reviews
# {0} must be replaced with the week number. e.g. week47
# This is necessary for the queries to work.
# {1} should be replaced with the date and weekday.
# But this is only to make it easier to understand which day you are looking at and is not strictly necessary.
# To use the template every bullet where you take notes must be connect to the appropriate link. e.g. summary-week48
# Otherwise it won't show up in the query.
# You can use Shift + Enter, indented bullets or copy the link to every bullet.
# I assume this template could easily be adapted to similar platforms like https://www.remnote.io/
daily_template = """- #{0} #[[{1}]] Summary 
    - #[[summary-{0}]] #[[{1}]]
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

# {0} must be replaced with the week number. e.g. week47
# It must follow the same format as the week in the daily review
# If you want to use this template to do monthly reviews, the same applies as for days:
# All notes must be connected to a bullet with a link like: summary-week47-review
week_template = """- {{{{[[query]]: {{and: [[summary-{0}]]}}}}}}
    - #[[summary-{0}-review]]
- {{{{[[query]]: {{and: [[events-{0}]]}}}}}}
    - #[[events-{0}-review]]
- {{{{[[query]]: {{and: [[better-{0}]]}}}}}}
    - #[[better-{0}-review]]
- {{{{[[query]]: {{and: [[bad-{0}]]}}}}}}
    - #[[bad-{0}-review]]
- {{{{[[query]]: {{and: [[good-{0}]]}}}}}}
    - #[[good-{0}-review]]
- {{{{[[query]]: {{and: [[best-{0}]]}}}}}}
    - #[[best-{0}-review]]
- {{{{[[query]]: {{and: [[progress-{0}]]}}}}}}
    - #[[progress-{0}-review]]
- {{{{[[query]]: {{and: [[gratitude-{0}]]}}}}}}
    - #[[gratitude-{0}-review]]"""

weekdays = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

def copy_daily():
    today = datetime.date.today() + datetime.timedelta(days=int(day_offset_input.value))
    week = "week" + str(today.isocalendar()[1])
    day = today.strftime("%Y-%m-%d") + " " + weekdays[today.weekday()]
    filled_template = daily_template.format(week, day)
    pyperclip.copy(filled_template)
    sys.exit()

def copy_weekly():
    today = datetime.date.today() + datetime.timedelta(days=int(day_offset_input.value))
    week = "week" + str(today.isocalendar()[1])
    filled_template = week_template.format(week)
    pyperclip.copy(filled_template)
    sys.exit()
# endregion

app = guizero.App(title="Templates", width=200, height=200, layout="grid")
# Allow for a day offset, in case you want to fill in a missed day or do your weekly review on Monday.
day_offset_label = guizero.Text(app, text="Day offset", grid=[0, 0])
day_offset_input = guizero.TextBox(app, text="0", grid=[1, 0])
daily_button = guizero.PushButton(app, copy_daily, text="Daily review", grid=[0, 1])
weekly_button = guizero.PushButton(app, copy_weekly, text="Weekly review", grid=[1, 1])
app.display()