import requests

import json
from collections import defaultdict

import config


class UserStates:
    init = 0
    confirmed = 10


class User:
    def __init__(self):
        self.used_scan = False

    def to_dict(self):
        return {
            "used_scan": self.used_scan
        }

    def from_dict(self, data):
        self.used_scan = data.get("used_scan", False)


def is_user_authorized(user_tg_id: int):
    result = requests.get(f"{config.INNOID_API_URL}/users/{user_tg_id}",
                          headers={"Authorization": f"Bearer {config.INNOID_API_TOKEN}"})
    if result.status_code == 200:
        return result.json()["is_authorized"]


def read_file():
    try:
        with open("users.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    result = defaultdict(User)
    for user_id in data:
        user = User()
        user.from_dict(data[user_id])
        result[int(user_id)] = user

    return result


def save_file():
    data = {str(user_id): user.to_dict() for user_id, user in users.items()}
    with open("users.json", "w") as f:
        json.dump(data, f)


users = read_file()
