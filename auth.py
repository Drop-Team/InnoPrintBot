import smtplib
import json
import random
import re

import config


class UserStates:
    init = 0
    requested_code = 1
    confirmed = 2


def read_file():
    try:
        with open("authorized_users.json") as f:
            authorized_users = json.load(f)
    except FileNotFoundError:
        authorized_users = {}
    data = {int(user_id): {"email": email, "state": UserStates.confirmed}
            for user_id, email in authorized_users.items()}
    return data


def save_file():
    authorized_users = {str(user_id): user_data["email"]
                        for user_id, user_data in users_data.items() if user_data["state"] == UserStates.confirmed}
    with open("authorized_users.json", "w") as f:
        json.dump(authorized_users, f)


def validate_email(email):
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return re.fullmatch(regex, email) and ("@innopolis.university" in email or "@innopolis.ru" in email)


def send_mail(user_id):
    def generate_code(user_id):
        code = str(random.randint(100000, 999999))
        users_data[user_id]["code"] = code
        return code

    code = generate_code(user_id)
    email = users_data[user_id]["email"]

    body = f"Hello.\n\nYour confirmation code is {code}.\n\nIf you have not requested it, please ignore this email."

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.ehlo()
    server.login(email_user, email_password)
    try:
        server.sendmail(sent_from, [email], f'Subject: {subject}\n\n{body}')
    except Exception:
        server.close()
        return False
    server.close()
    return True


def validate_code(user_id, code):
    return users_data[user_id].get("code", 0) == code


users_data = read_file()

email_user = config.EMAIL_LOGIN
email_password = config.EMAIL_PASSWORD
subject = "InnoPrintBot Email confirmation"
sent_from = email_user
