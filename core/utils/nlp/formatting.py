import inflect
import typing

def format_readable_date(dt):
    DAY_OF_MONTH = {
        1: 'first', 
        2: 'second', 
        3: 'third', 
        4: 'fourth', 
        5: 'fifth', 
        6: 'sixth', 
        7: 'seventh', 
        8: 'eighth', 
        9: 'ninth', 
        10: 'tenth', 
        11: 'eleventh', 
        12: 'twelfth', 
        13: 'thirteenth', 
        14: 'fourteenth', 
        15: 'fifteenth', 
        16: 'sixteenth', 
        17: 'seventeenth', 
        18: 'eighteenth', 
        19: 'nineteenth', 
        20: 'twentieth', 
        21: 'twenty first', 
        22: 'twenty second', 
        23: 'twenty third', 
        24: 'twenty fourth', 
        25: 'twenty fifth', 
        26: 'twenty sixth', 
        27: 'twenty seventh', 
        28: 'twenty eighth', 
        29: 'twenty ninth', 
        30: 'thirtieth', 
        31: 'thirty first'
    }
    
    month = dt.strftime("%B")
    day = dt.strftime(" %d").replace(" 0", "")
    year = dt.strftime("%Y")

    inf = inflect.engine()

    day = DAY_OF_MONTH[int(day)]
    century = inf.number_to_words(int(year[:2])).replace("-", " ")
    decade = inf.number_to_words(int(year[2:])).replace("-", " ")

    return f"{month} {day}, {century} {decade}"

def format_readable_time(dt, hour_format: str):
    time = dt.strftime(f"{hour_format}:%M")
    hour = time.split(":")[0].lstrip("0")
    minutes = time.split(":")[1]

    inf = inflect.engine()

    hour = inf.number_to_words(int(hour)).replace("-", " ")
    
    if minutes[0] == '0':
        minutes = minutes[1]
        if int(minutes) == 0:
            minutes = "o'clock"
        else:
            minutes = inf.number_to_words(int(minutes)).replace("-", " ")
            minutes = f"o'{minutes}"
    else:
        minutes = inf.number_to_words(int(minutes)).replace("-", " ")

    return f"{hour} {minutes}"

def format_readable_list(lst: typing.List):
    if len(lst) == 0:
        return "Nothing"
    elif len(lst) == 1:
        return lst[0]
    else:
        last_item = lst.pop(-1)
        return ', '.join(lst) + f" and {last_item}"

def format_seconds(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    time_strs = []
    if hours > 0:
        time_strs.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
    if minutes > 0:
        time_strs.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")
    if seconds > 0:
        time_strs.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")

    return format_readable_list(time_strs)