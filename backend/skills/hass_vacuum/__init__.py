from .hass_vacuum import HASS_Vacuum, build_skill, default_config

INTENTIONS = [
        {
            "action":"start_vacuum",
            "patterns":[
                "start the vacuum",
                "start vacuuming",
                "clean the floor",
                "clean the house",
                "vacuum the floor",
                "vacuum the house"
            ]
        },
        {
            "action":"pause_vacuum",
            "patterns":[
                "pause the vacuum"
            ]
        },
        {
            "action":"stop_vacuum",
            "patterns":[
                "stop the vacuum",
                "stop vacuuming",
            ]
        }
    ]