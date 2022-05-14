from bot.utils.jobs.states import JobState


class EditingState(JobState):
    show_expired_in = True


class ExpiredState(JobState):
    text = "Document expired."
    can_be_deleted = True
    show_parameters = False


class CancelledState(JobState):
    text = "Printing cancelled."
    can_be_deleted = True
    show_parameters = False


class WaitingInQueueState(JobState):
    text = "Waiting in queue..."


class ConnectingToPrinterState(JobState):
    text = "Connecting to printer..."


class PrinterNotRespondingState(JobState):
    text = "The printer is not responding."


class PrintingDocumentState(JobState):
    text = "Printing document..."


class CompletedState(JobState):
    text = "Completed, check printer."
    can_be_deleted = True
