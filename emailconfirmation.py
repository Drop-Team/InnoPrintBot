import smtplib
import json
import random

import config

def save_file():
    with open('authorized_users.json', 'w') as f:
        json.dump(confirmed_users, f)

def read_file():
    f = open('authorized_users.json', 'r')
    confirmed_users = json.load(f)
    f.close()
    return confirmed_users

def send_email(id, to):
    if not('@innopolis.university' in to or '@innopolis.ru' in to):
        return False

    code = random.randint(100000, 999999)
    user_codes[id] = [str(code), to]

    body = f'Your confirmation code is {code}'
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, [to], f'Subject: {subject}\n\n{body}')
    server.close()
    return True

def sign_up(id, code):
    if code == str(user_codes[id][0]):
        confirmed_users[str(id)] = user_codes[id][1]
        save_file()
        return True
    else:
        return False
    
def is_authorized(id):
    if str(id) in confirmed_users:
        return True
    return False


user_codes = dict()
confirmed_users = read_file()

gmail_user = config.email_login
gmail_password = config.email_password
subject = '@innoprintersbot email confirmation'
sent_from = gmail_user