import re


def check_consecutive(numbers):
    return sorted(numbers) == list(range(min(numbers), max(numbers) + 1))


def is_valid_tag(tag):
    # Special check for bad characters
    if any(bad_character in tag for bad_character in list("ёъыэ")):
        return False

    return re.compile(r"^[a-zа-яіїґ]{3,16}$").match(tag) is not None
