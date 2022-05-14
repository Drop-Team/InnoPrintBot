from bot.utils.jobs.states import JobState


class EditingState(JobState):
    show_expired_in = True


class ExpiredState(JobState):
    text = "Scanning expired."
    can_be_deleted = True
    show_parameters = False


class CancelledState(JobState):
    text = "Scanning cancelled."
    can_be_deleted = True
    show_parameters = False


class WaitingForDocumentState(JobState):
    text = "Scanning is in progress..."


class CompletedState(JobState):
    text = "Completed."
    can_be_deleted = True


class MultiScanEditingState(JobState):
    text = "In MultiScan mode. Select action."
    show_expired_in = True
