trail_data = {
        "Trail_1": {
            "is_allowed_start": False,
            "connections": {
                "Trail_2": {"distance": 1, "trail_name": "Canyon Trail"},
                "Trail_11": {"distance": 1.3, "trail_name": "Canyon Trail"},
                "Trail_12": {"distance": 1, "trail_name": "Mapel River Trail"}
            }
        },
        "Trail_2": {
            "is_allowed_start": False,
            "connections": {
                "Trail_1": {"distance": 1, "trail_name": "Canyon Trail"},
                "Trail_3": {"distance": 0.4, "trail_name": "Canyon Trail"}
            }
        },
        "Trail_3": {
            "is_allowed_start": False,
            "connections": {
                "Trail_2": {"distance": 0.4, "trail_name": "Canyon Trail"},
                "Trail_4": {"distance": 0.3, "trail_name": "Canyon Trail"},
                "Trail_8": {"distance": 0.5, "trail_name": "Winter Trail"}
            }
        },
        "Trail_4": {
            "is_allowed_start": False,
            "connections": {
                "Trail_3": {"distance": 0.4, "trail_name": "Canyon Trail"},
                "Trail_5": {"distance": 1.1, "trail_name": "Canyon Trail"},
                "Trail_7": {"distance": 0.5, "trail_name": "Twin Falls Trail"}
            }
        },
        "Trail_5": {
            "is_allowed_start": True,
            "connections": {
                "Trail_4": {"distance": 1.1, "trail_name": "Canyon Trail"},
                "Trail_6": {"distance": 0.3, "trail_name": "Upper North Falls"},
                "Trail_7": {"distance": 0.5, "trail_name": "North Rim Trail"}
            }
        },
        "Trail_6": {
            "is_allowed_start": False,
            "connections": {
                "Trail_5": {"distance": 0.3, "trail_name": "Upper North Falls"}
            }
        },
        "Trail_7": {
            "is_allowed_start": False,
            "connections": {
                "Trail_4": {"distance": 0.5, "trail_name": "Twin Falls Trail"},
                "Trail_5": {"distance": 0.8, "trail_name": "North Rim Trail"}
            }
        },
        "Trail_8": {
            "is_allowed_start": False,
            "connections": {
                "Trail_5": {"distance": 1, "trail_name": "Rim Trail"},
                "Trail_10": {"distance": 0.9, "trail_name": "Rim Trail"}
            }
        },
        "Trail_9": {
            "is_allowed_start": False,
            "connections": {
                "Trail_12": {"distance": 0.9, "trail_name": "Bike Path"},
                "Trail_9": {"distance": 1.6, "trail_name": "Bike Path"}
            }
        },
        "Trail_11": {
            "is_allowed_start": False,
            "connections": {
                "Trail_1": {"distance": 1.3, "trail_name": "Canyon Trail"},
                "Trail_12": {"distance": 0.3, "trail_name": "South Falls District"}
            }
        },
        "Trail_12": {
            "is_allowed_start": True,
            "connections": {
                "Trail_1": {"distance": 1, "trail_name": "Maple Ridge Trail"},
                "Trail_8": {"distance": 0.9, "trail_name": "Rim Trail"},
                "Trail_9": {"distance": 0.9, "trail_name": "Bike Path"},
                "Trail_11": {"distance": 0.3, "trail_name": "South Falls District"}, #find more exact later
                "Trail_13": {"distance": 0.5, "trail_name": "Bike Path"}
            }
        },
        "Trail_13": {
            "is_allowed_start": True,
            "connections": {
                "Trail_12": {"distance": 0.9, "trail_name": "Bike Path"}
            }
        }
    }
