from datetime import datetime
import numpy as np
import random


def current_time_integer() -> int:
    """
    Get the current time as an integer in the format %Y%m%d%H%M%S%f
    """
    now = datetime.now()
    date_string = now.strftime("%Y%m%d%H%M%S%f")
    date_int = int(date_string)
    return date_int


def generate_seed() -> int:
    """
    Get a new numpy seed from the current time.
    Numpy seeds are signed 32-bit integers.
    """
    return current_time_integer() % 2**32


def seed(value: int | None = None):
    """
    Set the random seed for numpy to a random number.
    """
    if value is None:
        value = generate_seed()
    np.random.seed(value)
    random.seed(value)


def get_seed() -> int:
    """
    Get the random seed for numpy.
    """
    return np.random.get_state()[1][0]
