from .default import Default, build_skill, default_config

INTENTIONS = [
        {
            "action":"introduction",
            "patterns":[
                "introduce yourself",
                "what are you", 
                "who are you",
                "explain who you are",
                "tell me about yourself"
            ]
        },
        {
            "action":"volume",
            "patterns":[
                "volume BLANK",
                "volume BLANK percent", 
                "set the volume to BLANK percent",
                "set the volume to",
                "change the volume to", 
                "volume down",
                "volume up",
                "volume up BLANK percent",
                "turn the volume down",
                "turn the volume up", 
                "turn down the volume",
                "turn up the volume"
            ]
        },
        {
            "action":"time",
            "patterns":[
                "what time is it",
                "whats the time",
                "what is the time",
                "can i get the time",
                "can you give me the time",
                "can i have the time",
                "i need the time",
                "i need to know what time it is",
                "tell me what time it is",
                "tell me what the time is",
                "tell me the time"
            ]
        },
        {
            "action":"date",
            "patterns":[
                "whats the date",
                "whats todays date",
                "what is the date",
                "what is todays date",
                "can i get the date",
                "can you give me the date",
                "can you give me todays date",
                "can i have the date",
                "i need the date",
                "tell me what date it is",
                "tell me what the date is",
                "tell me the date"
            ]
        },
        {
            "action":"day_of_week",
            "patterns":[
                "what day is it today",
                "what day is it",
                "what is the day",
                "what is today",
                "can i get the day",
                "can you give me the day",
                "can i have the day",
                "i need the day",
                "tell me what day it is",
                "tell me what the day is",
                "tell me the day"
            ]
        },
        {
            "action":"set_timer",
            "patterns":[
                "set a timer for",
                "set a timer",
                "set a BLANK timer",
                "set a BLANK minute timer",
                "set a BLANK hour timer",
                "set a timer for BLANK minutes",
                "set a timer for BLANK hours and BLANK minutes",
                "start a timer",
                "start a timer for BLANK",
                "start a timer for BLANK",
                "start a BLANK minute timer"
            ]
        },
        {
            "action":"time_remaining",
            "patterns":[
                "how much time is left",
                "how much time is left on the timer",
                "how long on the timer",
                "how much longer on the timer",
                "what is the time remaining"
            ]
        },
        {
            "action":"stop_timer",
            "patterns":[
                "stop the timer",
                "stop that timer",
                "cancel the timer",
                "cancel that timer",
                "forget the timer",
                "forget that timer"
            ]
        }
    ]