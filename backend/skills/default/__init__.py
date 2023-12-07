from .default import Default, build_skill, default_config

INTENTIONS = [
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
            "action":"hello",
            "patterns":[
                "hello", 
                "hi",
                "hey there", 
                "hello there",
                "hi there",
                "howdy", 
                "good morning",
                "good afternoon",
                "good evening",
                "good night",
                "goodnight"
            ]
        },
        {
            "action":"how_are_you",
            "patterns":[
                "how are you",
                "how are things",
                "how you doing today",
                "how are things going",
                "are you doing ok",
                "are you ok",
                "are you doing good",
                "how are you feeling today",
                "how are you today"
            ]
        },
        {
            "action":"whats_up",
            "patterns":[
                "whats up",
                "whats up there",
                "what is up",
                "whats up with you",
                "what is up with you",
                "what are you up to"
            ]
        },
        {
            "action":"goodbye",
            "patterns":[
                "goodbye",
                "bye bye",
                "cya", 
                "see ya", 
                "see you later", 
                "see ya later", 
                "i am leaving", 
                "have a good day", 
                "bye",
                "im going out",
                "im heading out",
                "ill see ya later",
                "im gonna go",
                "im going to go",
                "im going to head out"
            ]
        },
        {
            "action":"thank_you",
            "patterns":[
                "thanks",
                "thank you",
                "thanks a lot", 
                "thanks for your help", 
                "thanks for everything"
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
                "set a BLANK minute timer",
                "set a BLANK second timer",
                "start a timer",
                "start a timer for BLANK hours",
                "set a timer for BLANK minutes",
                "set a timer for BLANK seconds",
                "make a timer for",
                "make a timer"
            ]
        },
        {
            "action":"time_remaining",
            "patterns":[
                "how much time is left on the timer",
                "how much time is left",
                "how much time left",
                "how long on the timer",
                "how much longer on the timer",
                "what is the time remaining"
            ]
        },
        {
            "action":"stop",
            "patterns":[
                "stop",
                "cancel",
                "thats enough",
                "quiet",
                "be quiet",
                "shut up"
            ]
        }
    ]