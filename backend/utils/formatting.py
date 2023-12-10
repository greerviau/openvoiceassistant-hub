from datetime import datetime
import inflect

def format_readable_date(dt):
    month = dt.strftime("%B")
    day = dt.strftime("%d").replace(" 0", " ")
    year = dt.strftime("%Y")

    inf = inflect.engine()

    if int(day) in [1, 21, 31]:
        day = f"{day}st"
    elif int(day) in [2, 22]:
        day = f"{day}nd"
    elif int(day) in [3, 23]:
        day = f"{day}rd"
    else:
        day = f"{day}th"
        
    century = inf.number_to_words(int(year[:2])).replace("-", " ")
    decade = inf.number_to_words(int(year[2:])).replace("-", " ")

    return f"{month} {day}, {century}{decade}"

def format_readable_time(dt, hour_format: str):
    time = dt.strftime(f"{hour_format}:%M").lstrip("0")

    hour = time.split(":")[0]
    minutes = time.split(":")[1]

    inf = inflect.engine()

    hour = inf.number_to_words(int(hour)).replace("-", " ")
    minutes = inf.number_to_words(int(minutes)).replace("-", " ")

    return f"{hour} {minutes}"