from .hass_lights import HASS_Lights, build_skill, default_config

INTENTIONS = [
        {
            "action":"light_on",
            "patterns":[
                "lights on",
                "BLANK lights on",
                "turn the lights on in the BLANK",
                "turn on the lights",
                "turn on the BLANK lights",
                "turn the lights on",
                "turn the BLANK lights on",
                "switch the BLANK lights on"
                "switch the lights on",
                "switch on the lights"
            ]
        },
        {
            "action":"light_off",
            "patterns":[
                "lights off",
                "BLANK lights off",
                "turn the lights off in the BLANK",
                "turn off the lights",
                "turn off the BLANK lights",
                "turn the lights off",
                "turn the BLANK lights off",
                "switch the BLANK lights off"
                "switch the lights off",
                "switch off the lights"
            ]
        },
        {
            "action":"light_toggle",
            "patterns":[
                "lights",
                "lights",
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
                "lights BLANK percent",
                "lights BLANK percent brightness",
                "set the light brightness to BLANK percent",
                "set the light to BLANK percent brightness",
                "set the lights brightness to BLANK percent",
                "set the lights to BLANK percent brightness",
                "BLANK lights BLANK percent brightness"
                "set the BLANK light brightness to BLANK percent",
                "set the BLANK light to BLANK percent brightness",
                "set the BLANK lights brightness to BLANK percent",
                "set the BLANK lights to BLANK percent brightness",
                "set the BLANK to BLANK percent brightness",
            ]
        }
    ]