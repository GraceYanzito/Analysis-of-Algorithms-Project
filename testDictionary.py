travel_data = {
    "Salem": {
        "gps": (44.94, -123.03),
        "type": "Hub",
        "connections": {                  # Group routes here
            "Office": {"distance": 7, "type": "highway"},
            "Warehouse": {"distance": 4, "type": "local_road"}
        }
    },
    "Office": {
        "gps": (44.96, -123.01),
        "type": "Branch",
        "connections": {
            "Salem": {"distance": 7, "type": "highway"}
        }
    }
}
