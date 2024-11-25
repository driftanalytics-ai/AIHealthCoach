def count_characters_in_json(data):
    """Recursively counts characters in all string values in a JSON-like dictionary or list."""
    char_count = 0

    if isinstance(data, dict):
        for key, value in data.items():
            char_count += count_characters_in_json(value)
    elif isinstance(data, list):
        for item in data:
            char_count += count_characters_in_json(item)
    elif isinstance(data, str):
        char_count += len(data)

    return char_count
