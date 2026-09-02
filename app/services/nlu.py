import re

def extract_city(message: str):
    """
    Extract city from sentences like:
    Weather in Delhi
    Weather in Guwahati
    """

    match = re.search(r"in\s+([A-Za-z ]+)", message)

    if match:
        return match.group(1).strip()

    return None