from abc import ABC


class JobState(ABC):
    """State of Job"""

    text: str = None
    can_be_deleted: bool = False
    show_parameters: bool = True
    show_expired_in: bool = False
    show_ad: bool = False
