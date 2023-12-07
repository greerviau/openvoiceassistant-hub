from .hass_lights import HASS_Lights, build_skill, default_config

INTENTIONS = [
        {
            "action":"light_on",
            "patterns":[
                "lights on",
                "BLANK lights on",
                "turn on the lights",
                "turn on the BLANK lights",
                "turn on BLANK lights",
                "turn the lights on",
                "turn the BLANK lights on"
            ]
        },
        {
            "action":"light_off",
            "patterns":[
                "lights off",
                "BLANK lights off",
                "turn off the lights",
                "turn off the BLANK lights",
                "turn off BLANK lights",
                "turn the lights off",
                "turn the BLANK lights off"
            ]
        },
        {
            "action":"light_toggle",
            "patterns":[
                "lights please",
                "BLANK lights",
                "toggle the lights",
                "toggle the BLANK lights",
                "get the lights",
                "get the BLANK lights"
            ]
        },
        {
            "action":"light_brightness",
            "patterns":[
                "set the BLANK lights to BLANK percent",
                "set the BLANK lights to BLANK percent brightness",
                "BLANK lights BLANK percent",
                "BLANK lights BLANK percent brightness"
            ]
        }
    ]