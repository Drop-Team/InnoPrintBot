import re
import random
import smtplib

from bot.users import users
import config

email_user = config.EMAIL_LOGIN
email_password = config.EMAIL_PASSWORD
subject = "InnoPrintBot Email confirmation"
body = "Hello.\n\n" \
       "Your confirmation code for @InnoPrintBot is {}.\n\n" \
       "If you have not requested it, please ignore this email."
sent_from = email_user


def validate_email(email):
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    domains = ["innopolis.university", "innopolis.ru"]
    return re.fullmatch(regex, email) and (any([email.endswith("@" + domain) for domain in domains]))


def set_email(user_id, email):
    users[user_id].email = email


def generate_code(user_id):
    code = str(random.randint(100000, 999999))
    users[user_id].confirmation_code = code
    return code


def validate_code(user_id, code):
    return str(users[user_id].confirmation_code) == str(code)


def send_mail(user_id):
    code = generate_code(user_id)
    email = users[user_id].email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.ehlo()
    server.login(email_user, email_password)
    try:
        server.sendmail(sent_from, [email], f"Subject: {subject}\n\n"
                                            f"{body.format(code)}")
    except Exception:
        server.close()
        return False
    server.close()
    return True
