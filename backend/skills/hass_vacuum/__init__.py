from .hass_vacuum import HASS_Vacuum, build_skill, default_config

INTENTIONS = [
        {
            "action":"start_vacuum",
            "patterns":[
                "start the vacuum",
                "vacuum the floor",
                "start vacuuming the floor"
            ]
        },
        {
            "action":"stop_vacuum",
            "patterns":[
                "stop the vacuum",
                "stop vacuuming",
                "stop vacuuming the floor"
            ]
        },
        {
            "action":"return_to_base",
            "patterns":[
                "send the vacuum home",
                "send the vacuum back to base"
            ]
        }
    ]