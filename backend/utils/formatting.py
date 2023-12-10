from datetime import datetime
import inflect

def format_readable_date(dt):
    month = dt.strftime("%B")
    day = dt.strftime("%d").replace(" 0", " ")
    year = dt.strftime("%Y")

    inf = inflect.engine()

    day = inf.number_to_words(int(day))
    century = inf.number_to_words(int(year[:2]))
    decade = inf.number_to_words(int(year[2:]))

    return f"{month} {day}, {century}{decade}"

def format_readable_time(dt, hour_format: str):
    time = dt.strftime(f"{hour_format}:%M").lstrip("0")

    hour = time.split(":")[0]
    minutes = time.split(":")[1]

    inf = inflect.engine()

    hour = inf.number_to_words(int(hour))
    minutes = inf.number_to_words(int(minutes))

    return f"{hour} {minutes}"