import datetime
import json
import redis
from typing import Optional, Dict, Any


def seconds_until_next_monday() -> int:
    now = datetime.datetime.now()
    days_until_monday = (7 - now.weekday()) % 7
    if days_until_monday == 0:  # Если сегодня понедельник
        days_until_monday = 7  # Устанавливаем на следующую неделю
    next_monday = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=days_until_monday)
    return int((next_monday - now).total_seconds())


class Cache:
    def __init__(self, host: str, port: int):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)

    def set_users_group(self, user_id: int, group: str) -> None:
        self.r.set(f"user:{user_id}:group", group)

    def get_users_group_id(self, user_id: int) -> Optional[str]:
        return self.r.get(f"user:{user_id}:group")

    def set_group_schedule(self, group_id: str, schedule: Dict[str, Any]) -> None:
        expire_time = seconds_until_next_monday()
        if expire_time <= 0:
            raise ValueError("Время истечения должно быть положительным")
        self.r.set(
            name=f"group:{group_id}:schedule",
            value=json.dumps(schedule),
            ex=expire_time
        )

    def get_group_schedule(self, group_id: str) -> Optional[Dict[str, Any]]:
        json_schedule = self.r.get(f"group:{group_id}:schedule")
        return json.loads(json_schedule) if json_schedule else None

    def get_users_count(self) -> int:
        return len(self.r.keys(pattern="user:*"))

    def get_groups_count(self) -> int:
        return len(self.r.keys(pattern="group:*"))
