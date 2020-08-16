"""
Utility functions.

.. autosummary::
    ~C2F
    ~run_in_thread
    ~smooth

"""

__all__ = "C2F run_in_thread smooth".split()

import threading


def C2F(celsius):
    """Convert celsius to fahrenheit."""
    return celsius * 9 / 5 + 32


def run_in_thread(func):
    """
    (decorator) run ``func`` in thread
    USAGE::

       @run_in_thread
       def progress_reporting():
           logger.debug("progress_reporting is starting")
           # ...
       #...
       progress_reporting()   # runs in separate thread
       #...

    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def smooth(reading, factor, previous):
    """
    apply smoothing function

    ::

        smoothed = k*raw + (1-k)*previous

    """
    if previous is None:
        value = reading
    else:
        value = factor*previous + (1-factor)*reading
    return value
