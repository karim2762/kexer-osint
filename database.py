import json

def load_sites():
    with open("sites.json") as f:
        return json.load(f)
