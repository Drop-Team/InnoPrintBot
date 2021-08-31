from prometheus_client import Counter, Gauge


def save_auth_users_count(data):
    Metrics.authorized_users_total.set(len(data))


class Metrics:
    printing_enabled = Gauge("printing_enabled", "on or off")

    authorized_users_total = Gauge("authorized_users_total", "users who confirmed email")

    errors = Counter("errors", "Errors count")

    start_command = Counter("start_command", "Using /start command", ["type"])
    start_command.labels("success")

    help_command = Counter("help_command", "Using /help command", ["type"])
    help_command.labels("success")

    code_sending = Counter("code_sending", "Trying to send code", ["type"])
    code_sending.labels("cooldown")
    code_sending.labels("error_sending_letter")
    code_sending.labels("success")

    email_setting = Counter("email_setting", "Trying to set email", ["type"])
    email_setting.labels("validation_failed")
    email_setting.labels("success")

    email_changing = Counter("email_changing", "Trying to change email", ["type"])
    email_changing.labels("already_authorized")
    email_changing.labels("success")

    code_attempt = Counter("code_attempt", "Trying to attempt code", ["type"])
    code_attempt.labels("validation_failed")
    code_attempt.labels("cooldown")
    code_attempt.labels("inactive")
    code_attempt.labels("incorrect")
    code_attempt.labels("success")

    code_resending = Counter("code_resending", "Trying to resend code", ["type"])
    code_resending.labels("email_not_set")
    code_resending.labels("already_authorized")
    code_resending.labels("success")

    printing = Counter("printing", "Trying to print", ["type"])
    printing.labels("not_doc")
    printing.labels("cooldown")
    printing.labels("big_file")
    printing.labels("success")
