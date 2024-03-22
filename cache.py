import datetime
import json

import redis


def seconds_until_next_monday():
    today = datetime.date.today()
    days_until_next_monday = (7 - today.weekday() + 0) % 7  # Monday is 0 in Python's weekday() function
    next_monday = today + datetime.timedelta(days=days_until_next_monday)
    next_monday_midnight = datetime.datetime.combine(next_monday, datetime.time.min)
    now = datetime.datetime.now()
    time_until_next_monday = next_monday_midnight - now
    return int(time_until_next_monday.total_seconds())


class Cache:
    def __init__(self, host, port):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)

    def set_users_group(self, user_id, group):
        self.r.set(f"user:{user_id}:group", group)

    def get_users_group_id(self, user_id):
        return self.r.get(f"user:{user_id}:group")

    def set_group_schedule(self, group_id, schedule):
        self.r.set(name=f"group:{group_id}:schedule", value=json.dumps(schedule), ex=seconds_until_next_monday())

    def get_group_schedule(self, group_id):
        json_schedule = self.r.get(f"group:{group_id}:schedule")
        if json_schedule is None:
            return None
        return json.loads(json_schedule)

    def get_users_count(self):
        users = self.r.keys(pattern="user:*")
        return len(users)

    def get_groups_count(self):
        groups = self.r.keys(pattern="group:*")
        return len(groups)
