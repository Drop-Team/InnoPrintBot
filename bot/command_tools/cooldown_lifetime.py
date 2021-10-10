from datetime import datetime


class BaseCheck:
    cooldown = None
    lifetime = None


class Checks:
    class CodeSending(BaseCheck):
        cooldown = 30
        lifetime = 10 * 60

    class CodeAttempt(BaseCheck):
        cooldown = 5


def set_check(user_id, cd_type):
    """Updating check for user"""
    data[(user_id, cd_type)] = datetime.now()


def validate_cooldown(user_id, check):
    """Returns False if user is under cooldown, True - if not"""
    last_record = data.get((user_id, check), None)
    if last_record is None:
        return True
    if int((datetime.now() - last_record).total_seconds()) > check.cooldown:
        return True
    return False


def validate_lifetime(user_id, check):
    """Returns False if lifetime is passed, True - if not"""
    last_record = data.get((user_id, check), None)
    if last_record is None:
        return True
    if int((datetime.now() - last_record).total_seconds()) > check.lifetime:
        return False
    return True


def get_remain_time(user_id, check):
    """Returns the time until cooldown reset in seconds"""
    last_record = data.get((user_id, check), None)
    if last_record is None:
        return 0
    difference = int((datetime.now() - last_record).total_seconds())
    return check.cooldown - difference


data = dict()
