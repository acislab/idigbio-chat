from redis import Redis
from flask import Flask
from storage.fake_redis import FakeRedis
import os

class FlaskRedis:
    inst: Redis

    def init_app(self, app: Flask):
        if "REDIS" not in app.config or app.config["REDIS"]["PORT"] == 0:
            self.inst = FakeRedis().redis
        else:
            self.inst = Redis.from_url(f"redis://:{os.getenv('REDIS_SECRET')}@{os.getenv('REDIS_HOST')}:6379/2")
