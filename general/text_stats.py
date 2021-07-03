import sys
import re
from enum import Enum
import win32clipboard

win32clipboard.OpenClipboard()
try:
    text = win32clipboard.GetClipboardData()
except TypeError:
    # Clip board data is not available
    sys.exit(-1)
win32clipboard.CloseClipboard()


class State:
    def __init__(self):
        self.words = []
        self.sentences = []
        self.word_length = 0
        self.sentence_length = 0

    def __str__(self):
        return "Words: {}\nSentences: {}".format(self.words, self.sentences)

    def avg_word_length(self):
        word_sum = 0
        for word in self.words:
            word_sum += word
        return round(word_sum / len(self.words), 2)

    def avg_sentence_length(self):
        sentence_sum = 0
        for sentence in self.sentences:
            sentence_sum += sentence
        return round(sentence_sum / len(self.sentences), 2)


def end_sentence(state):
    end_word(state)
    if state.sentence_length > 0:
        state.sentences.append(state.sentence_length)
        state.sentence_length = 0


def end_word(state):
    if state.word_length > 0:
        state.words.append(state.word_length)
        state.word_length = 0
        state.sentence_length += 1


def analyze(text, state):
    for char in text:
        if re.search("[a-z]|[A-Z]|ä|Ä|ö|Ö|ü|Ü", char) is not None:
            state.word_length += 1
            continue
        if char == "." or char == "!" or char == "?" or char == ":":
            end_sentence(state)
            continue
        else:
            end_word(state)
            continue
    end_sentence(state)


state = State()
analyze(text, state)

result = "Avg word length: {}\n".format(state.avg_word_length())
result += "Avg sentence length: {}".format(state.avg_sentence_length())

file = open("tmp_result", "w")
file.write(result)
file.close()