import os


class Config:
    def __init__(self):
        self.telegram_api_token = os.getenv('TELEGRAM_API_TOKEN')
        self.telegram_admin_id = os.getenv('TELEGRAM_ADMIN_ID')

        self.redis_host = os.getenv('REDIS_HOST')
        self.redis_port = os.getenv('REDIS_PORT')
