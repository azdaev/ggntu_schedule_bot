import os
from typing import Optional


class Config:
    def __init__(self):
        self.telegram_api_token: str = os.getenv('TELEGRAM_API_TOKEN', '')
        self.telegram_admin_id: Optional[int] = int(os.getenv('TELEGRAM_ADMIN_ID', 0)) or None
        self.redis_host: str = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port: int = int(os.getenv('REDIS_PORT', 6379))

    def validate(self) -> None:
        if not self.telegram_api_token:
            raise ValueError("TELEGRAM_API_TOKEN не установлен")
        if not self.redis_host:
            raise ValueError("REDIS_HOST не установлен")
