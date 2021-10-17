import json
from collections import defaultdict

from bot.metrics import Metrics


def save_users_metrics(data):
    users_metrics = {}
    state_names = {
        UserStates.init: "init",
        UserStates.requested_code: "requested_code",
        UserStates.confirmed: "confirmed"
    }
    for user in data.values():
        state = state_names.get(user.state, "Unknown")
        users_metrics[state] = users_metrics.get(state, 0) + 1

    for state, value in users_metrics.items():
        Metrics.users.labels(state).set(value)


class UserStates:
    init = 0
    requested_code = 1
    confirmed = 10


class User:
    def __init__(self, email=None):
        self.state = UserStates.init
        self.email = email
        self.confirmation_code = None
        self.used_scan = False

    def to_dict(self):
        return {
            "state": self.state,
            "email": self.email,
            "used_scan": self.used_scan
        }

    def from_dict(self, data):
        self.state = data["state"]
        self.email = data["email"]
        self.used_scan = data.get("used_scan", False)


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

    save_users_metrics(result)

    return result


def save_file():
    data = {str(user_id): user.to_dict() for user_id, user in users.items()}
    with open("users.json", "w") as f:
        json.dump(data, f)

    save_users_metrics(users)


users = read_file()
