import re

def analyze_username(username):

    data = {}

    data["length"] = len(username)
    data["has_numbers"] = bool(re.search(r"\d", username))
    data["has_special_chars"] = bool(re.search(r"[^a-zA-Z0-9]", username))

    years = re.findall(r"(19\d{2}|20\d{2})", username)
    data["possible_birth_year"] = years[0] if years else None

    if len(username) <= 5:
        data["risk_level"] = "Rare Username"
    elif len(username) <= 10:
        data["risk_level"] = "Moderate"
    else:
        data["risk_level"] = "Common"

    return data
