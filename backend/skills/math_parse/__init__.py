from .mathparse import Mathparse, build_skill, default_config

INTENTIONS = [
        {
            "action":"equation",
            "patterns":[
                "what is BLANK plus BLANK",
                "whats BLANK plus BLANK",
                "what is the squareroot of BLANK",
                "what is the square root of BLANK",
                "whats the squareroot of BLANK",
                "whats the square root of BLANK",
                "what is BLANK times BLANK",
                "whats BLANK times BLANK",
                "what is BLANK minus BLANK",
                "whats BLANK minus BLANK"
            ]
        }
    ]