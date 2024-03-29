import string
import datetime
import typing
import re
import logging
logger = logging.getLogger("preprocessing")

from word2number import w2n
from nltk.corpus import stopwords
from rapidfuzz import fuzz
from rapidfuzz import utils as fuzzutils

STOPWORDS = list(set(stopwords.words("english")))
STOPWORDS.extend(["some", "what"])
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_OF_MONTH = {
    "first":1, 
    "second":2, 
    "third":3, 
    "fourth":4, 
    "fifth":5, 
    "sixth":6, 
    "seventh":7, 
    "eighth":8, 
    "ninth":9, 
    "tenth":10, 
    "eleventh":11, 
    "twelfth":12, 
    "thirteenth":13, 
    "fourteenth":14, 
    "fifteenth":15, 
    "sixteenth":16, 
    "seventeenth":17, 
    "eighteenth":18, 
    "nineteenth":19, 
    "twentieth":20, 
    "twenty first":21,
    "twenty second":22,
    "twenty third":23,
    "twenty fourth":24,
    "twenty fifth":25,
    "twenty sixth":26,
    "twenty seventh":27,
    "twenty eighth":28,
    "twenty ninth":29,
    "thirtieth":30,
    "thirty first":31
}
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

def try_parse_word_number(word: str):
    try:
        return str(w2n.word_to_num(word))
    except:
        return word

def parse_time(text: str):
    text = text.lower()
    time = None
    time_str = ""
    try:
        time = datetime.strptime(text, "%H:%M %p")
        return (int(time.strftime("%I%M")), time, text, True)
    except:
        pass

    try:
        time = datetime.strptime(text, "%H %p")
        return (int(time.strftime("%I")), time, text, True)
    except:
        pass

    try:
        time = datetime.strptime(text, "%H:%M")
        return (int(time.strftime("%I%M")), time, text, True)
    except:
        pass

    try:
        time = datetime.strptime(text, "%H")
        return (int(time.strftime("%I")), time, text, True)
    except:
        pass

    numbers = []
    pm = False
    am = False
    tod = False
    for word in text.split():
        if word.isdigit():
            numbers.append(int(word))
        else:
            try:
                numbers.append(w2n.word_to_num(word))
            except:
                pass
        if "pm" in word:
            pm = True
            tod = True
        elif "am" in word:
            am = True
            tod = True

    if len(numbers) > 0:
        try:
            if pm:
                numbers[0] += 12
            time = datetime.time(*numbers)
            time_str = time.strftime("%I:%M %p")
        except:
            pass
    if time:
        return (int(time.strftime("%I%M")), time, time_str, tod)
    return (None, None, "", False)

def parse_date(text: str):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today, "today"
    
    if text.count("tomorrow") > 0:
        return today + datetime.timedelta(days=1), "tomorrow"

    day = -1
    day_str = ""
    day_of_week = -1
    day_of_week_str = ""
    month = -1
    month_str = ""
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
            month_str = MONTHS[month-1]
        elif word in DAYS:
            day_of_week = DAYS.index(word)
            day_of_week_str = DAYS[day_of_week]
        elif word.isdigit():
            day = int(word)
            day_str = word
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                        day_str = word
                    except:
                        pass

    for word, number in DAY_OF_MONTH.items():
        if word in text:
            day = DAY_OF_MONTH[word]
            day_str = word
            break

    if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
        year = year+1

    if month == -1 and day != -1:  # if we didn"t find a month, but we have a day
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    # if we only found a dta of the week
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7
                day_of_week_str = "next "+day_of_week_str
        return today + datetime.timedelta(dif), day_of_week_str

    if day != -1:
        return datetime.date(month=month, day=day, year=year), f"{month_str} {day_str}"

    return None, None

def remove_stop_words(phrase: str) -> str:
    for word in STOPWORDS:
        phrase = phrase.replace(word, "")
    return phrase.strip()

def extract_numbers(sentence: str) -> str:
    return re.findall(r"\d+", sentence)

def find_string_match(guess: str, possibilities: typing.List[str]) -> str:
    if not possibilities:
        return None
    conf = 0
    answer = None
    for p in possibilities:
        r = fuzz.WRatio(guess, p, processor=fuzzutils.default_process)
        if r > conf:
            conf = r
            answer = p
    return answer

def replace_punctuation(text: str, replace_with: str = "") -> str:
    return re.sub("[^a-zA-Z0-9 \n\.]", replace_with, text)

def get_after(text: str, split_token: str) -> str:
    return text.split(split_token)[-1]

def clean_text(text: str) -> str:
    text = text.lower()
    text = text.replace("%", " percent")
    text = text.replace("-", " ")
    table = str.maketrans("", "", string.punctuation)
    text = " ".join([w.translate(table) for w in text.split()])
    text = text.strip()
    return text

def preprocess_text(text: str) -> str:
    text = " ".join([try_parse_word_number(word) for word in text.split()])
    return text

def encode_command(command: str, vocab: typing.List[str]) -> str:
    last_blank = False
    words = []
    for word in command.split():
        if word not in vocab:
            if not last_blank:
                last_blank = True
                words.append("BLANK")
        else:
            last_blank = False
            words.append(word)
    if len(words) > 2:
        if words[0] == "BLANK":
            words.pop(0)
    return " ".join(words)

def remove_words(self, text: str, words: typing.List[str]) -> str:
    for word in words:
        text = text.replace(word, "").strip()
    return text

if __name__ == "__main__":
    while True:
        c = input("-> ")
        if c in ["stop"]: break
        parsed = information_extraction(c)