import datetime
import json
import redis


def seconds_until_next_monday():
    # count seconds until end of day
    now = datetime.datetime.now()
    end_of_today = now.replace(hour=23, minute=59, second=59)
    until_end_of_today = (end_of_today - now).total_seconds()
    print(now)

    # count days left in week
    today_weekday = datetime.date.today().weekday()
    print(today_weekday)
    
    days_until_monday = 7 - today_weekday - 1
    seconds_until_next_monday = days_until_monday * 24 * 60 * 60 + until_end_of_today

    return int(seconds_until_next_monday)


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
