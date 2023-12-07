from .openweathermap import OpenWeatherMap, build_skill, default_config

INTENTIONS = [
        {
            "action":"weather",
            "patterns":[
                "whats the weather", 
                "show me the weather", 
                "tell me the weather", 
                "give me the weather", 
                "can i have the weather", 
                "hows the weather", 
                "how is the weather", 
                "hows it look outside",
                "whats it looking like outside",
                "can i get the weather",
                "can you get me the weather",
                "whats the weather like in",
                "how is the weather in"
            ]
        },
        {
            "action":"sky",
            "patterns":[
                "is it sunny outside", 
                "is it cloudy",
                "is it raining",
                "is it raining",
                "is it going to rain",
                "is it gonna be nice",
                "is it overcast",
                "is it going to be overcast",
                "what will the skies be like",
                "what are the skies looking like",
                "how is the sky looking",
                "what do the skies look like",
                "how are the skies in",
                "what are the skies like in",
                "whats the sky like"
            ]
        },
        {
            "action":"air",
            "patterns":[
                "what is the air like",
                "what are the air conditions",
                "is it humid",
                "is it humid outside",
                "is it muggy",
                "is it muggy outside",
                "is is looking muggy",
                "is it dry",
                "is it dry outside",
                "is it looking dry outside",
                "give me the air conditions",
                "give me the humidity",
                "whats the humidity",
                "what is the humidity"
            ]
        },
        {
            "action":"temperature",
            "patterns":[
                "is it cold outside", 
                "is it hot today",
                "whats the temperature outside",
                "whats the temp",
                "what is the temperature",
                "whats the temperature in",
                "whats the temp in",
                "how hot is it",
                "how cold is it",
                "is it hot outside",
                "what is the temperature outside",
                "whats the heat"
            ]
        }
    ]