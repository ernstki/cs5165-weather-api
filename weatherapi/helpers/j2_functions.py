from datetime import datetime as dt
from humanize import naturaltime, naturaldate

__all__ = [ 'humantime', 'humandate', 'currentyear' ]


def humantime(dt):
    """
    Format a datetime time in a human-friendly way
    """
    return naturaltime(dt)


def humandate(dt):
    """
    Format a datetime date in a human-friendly way
    """
    return naturaldate(dt)


def currentyear():
    """
    Return the current year
    """
    return dt.now().year

