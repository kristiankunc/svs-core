from datetime import datetime


def to_goated_time_format(dt: datetime) -> str:
    """Convert a datetime object to a goated time format string.

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        str: The formatted Goated time string.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def indentate(text: str, level: int = 0) -> str:
    """Generate indentation spaces.

    Args:
        text (str): The text to indent.
        level (int): The indentation level.

    Returns:
        str: A string with indentation applied.
    """
    indentation = " " * (level * 4)
    res = indentation + text.replace("\n", "\n" + indentation)
    return res
