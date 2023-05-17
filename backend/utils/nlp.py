import numpy as np
import string
import datetime
from word2number import w2n
from nltk.corpus import stopwords
import spacy
from spacy.matcher import DependencyMatcher

import typing

nlp = spacy.load('en_core_web_sm')

STOPWORDS = list(set(stopwords.words('english')))
STOPWORDS.extend(['some', 'what'])
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june','july', 'august', 'september','october', 'november', 'december']
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAY_OF_MONTH = {
    'first':1, 
    'second':2, 
    'third':3, 
    'fourth':4, 
    'fifth':5, 
    'sixth':6, 
    'seventh':7, 
    'eighth':8, 
    'ninth':9, 
    'tenth':10, 
    'eleventh':11, 
    'twelfth':12, 
    'thirteenth':13, 
    'fourteenth':14, 
    'fifteenth':15, 
    'sixteenth':16, 
    'seventeenth':17, 
    'eighteenth':18, 
    'nineteenth':19, 
    'twentieth':20, 
    'twenty first':21,
    'twenty second':22,
    'twenty third':23,
    'twenty fourth':24,
    'twenty fifth':25,
    'twenty sixth':26,
    'twenty seventh':27,
    'twenty eighth':28,
    'twenty ninth':29,
    'thirtieth':30,
    'thirty first':31
}
DAY_EXTENTIONS = ['rd', 'th', 'st', 'nd']

def try_parse_word_number(word):
    try:
        return w2n.word_to_num(word)
    except:
        if isinstance(word, int) or isinstance(word, float):
            return word
        else:
            return None

def parse_time(text):
    text = text.lower()
    time = None
    time_str = ''
    try:
        time = datetime.strptime(text, '%H:%M %p')
        return (int(time.strftime('%I%M')), time, text, True)
    except:
        pass

    try:
        time = datetime.strptime(text, '%H %p')
        return (int(time.strftime('%I')), time, text, True)
    except:
        pass

    try:
        time = datetime.strptime(text, '%H:%M')
        return (int(time.strftime('%I%M')), time, text, True)
    except:
        pass

    try:
        time = datetime.strptime(text, '%H')
        return (int(time.strftime('%I')), time, text, True)
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
        if 'pm' in word:
            pm = True
            tod = True
        elif 'am' in word:
            am = True
            tod = True

    if len(numbers) > 0:
        try:
            if pm:
                numbers[0] += 12
            time = datetime.time(*numbers)
            time_str = time.strftime('%I:%M %p')
        except:
            pass
    if time:
        return (int(time.strftime('%I%M')), time, time_str, tod)
    return (None, None, '', False)

def parse_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count('today') > 0:
        return today, 'today'
    
    if text.count('tomorrow') > 0:
        return today + datetime.timedelta(days=1), 'tomorrow'

    day = -1
    day_str = ''
    day_of_week = -1
    day_of_week_str = ''
    month = -1
    month_str = ''
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

    # THE NEW PART STARTS HERE
    if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
        year = year+1

    # This is slighlty different from the video but the correct version
    if month == -1 and day != -1:  # if we didn't find a month, but we have a day
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
            if text.count('next') >= 1:
                dif += 7
                day_of_week_str = 'next '+day_of_week_str
        return today + datetime.timedelta(dif), day_of_week_str

    if day != -1:  # FIXED FROM VIDEO
        return datetime.date(month=month, day=day, year=year), f'{month_str} {day_str}'

    return None, None

def named_entity_recognition(sentence):
    doc = nlp(sentence)

    parsed = {}

    for ent in doc.ents:
        parsed[ent.label_] = ent.text

    return parsed

def information_extraction(sentence):
    doc = nlp(sentence)

    parsed = {}
    parsed["SUBJECT"], parsed["OBJECT"], parsed["COMP"] = [], [], []

    for token in doc:
        #print(f"{token.text} -> {token.dep_}")
        if (token.dep_=='nsubj'):
            parsed["SUBJECT"].append(token.text)

        elif (token.dep_=='dobj'):
            parsed["OBJECT"].append(token.text)

        elif (token.dep_=='compound'):
            parsed["COMP"].append(token.text)

    parsed["ENTITIES"] = named_entity_recognition(sentence)

    parsed['NOUN_CHUNKS'] = []
    for chunk in doc.noun_chunks:
        parsed['NOUN_CHUNKS'].append(chunk.text)

    object_pattern = [
        {
            "RIGHT_ID": "target",
            "RIGHT_ATTRS": {"POS": "NOUN"}
        },
        # founded -> subject
        {
            "LEFT_ID": "target",
            "REL_OP": ">",
            "RIGHT_ID": "modifier",
            "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "nummod"]}}
        }
    ]

    matcher = DependencyMatcher(nlp.vocab)
    matcher.add("OBJECT", [object_pattern])   

    for match_id, (target, modifier) in matcher(doc):
        parsed["MOD_OBJECT"] = ' '.join([doc[modifier].text, doc[target].text])

    return parsed

'''
RELATED TO INTENT CLASSIFICATION
'''

def get_after(text, token):
    return text.split(token)[-1]

def clean_text(text):
    table = str.maketrans('', '', string.punctuation)
    text = text.lower()
    text = ' '.join([w.translate(table) for w in text.split()])
    text = text.strip()
    return text

def encode_bow(text, vocab):
    encoded = np.zeros(len(vocab))
    for word in text.split():
        if word in vocab.keys():
            encoded[vocab[word]] = 1
    return np.array(encoded)

def encode_word_vec(text, vocab):
    encoded = np.zeros(len(text.split()))
    for i, word in enumerate(text.split()):
        if word in vocab.keys():
            encoded[i] = vocab[word]
    return np.array(encoded)

def pad_sequence(encoded, seq_length):
    padding = np.zeros(seq_length)
    if len(encoded) > seq_length:
        padding = encoded[:seq_length]
    else:
        padding[:len(encoded)] = encoded
    return padding

if __name__ == '__main__':
    c = "turn on the kitchen lights"
    parsed = information_extraction(c)
    print(parsed)