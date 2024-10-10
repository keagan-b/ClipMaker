"""
Developed by Keagan B
ClipMaker -- utils.py

Utility functions

"""


def get_milliseconds_from_time(time_value: str) -> int:
    """
    Converts a timestamp to milliseconds
    :param time_value: The time value in a mm:ss format
    :return: Number of milliseconds
    """
    try:
        minutes, seconds = list(map(int, time_value.split(":")))
    except ValueError:
        return 0

    seconds += minutes * 60

    return seconds * 1000


def get_time_from_milliseconds(milliseconds: int) -> str:
    """
    Converts a milliseconds to timestamp
    :param milliseconds: Millisecond count
    :return: Time in a mm:ss format
    """
    # make sure a current clip exists
    seconds = milliseconds // 1000

    minutes = seconds // 60
    seconds %= 60

    return f"{minutes:02}:{seconds:02}"
