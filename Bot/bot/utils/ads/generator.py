from random import choice

from .ads import ads


def get_ad() -> str:
    """Randomly get ad which should be shown after job completion"""

    return choice(ads)
