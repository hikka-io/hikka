import re


def is_valid_css_background(v: str | None) -> bool:
    # Allow None since field is optional
    if v is None:
        return True

    v = v.strip()

    # Just in case
    if len(v) > 4096:
        return False

    # Explicitly disallow dangerous stuff
    if re.search(
        r"^\s*(javascript|data|vbscript|file|url|important):", v, re.IGNORECASE
    ):
        return False

    # Allow hex codes
    # What could possibly go wrong
    if re.match(r"^#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", v):
        return True

    # Allowed types of background
    allowed_patterns = [
        r"^rgb\s*\(.+\)$",
        r"^rgba\s*\(.+\)$",
        r"^hsl\s*\(.+\)$",
        r"^hsla\s*\(.+\)$",
        r"^(repeating-)?linear-gradient\s*\(.+\)$",
        r"^(repeating-)?radial-gradient\s*\(.+\)$",
        r"^conic-gradient\s*\(.+\)$",
    ]

    for pattern in allowed_patterns:
        if re.match(pattern, v, re.IGNORECASE):
            return True

    # Fail by default because users are clever bastards
    return False
