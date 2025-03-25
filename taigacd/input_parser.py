import json


def parse_input(json_path: str) -> dict:
    """Parse JSON file and return parameters as a dictionary."""
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
