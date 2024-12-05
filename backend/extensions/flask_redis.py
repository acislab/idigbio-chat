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
            port = app.config["REDIS"]["PORT"]
            host = app.config["REDIS"]["HOST"]
            secret = os.getenv('REDIS_SECRET')
            database_number = app.config["REDIS"]["DATABASE_NUMBER"]
            self.inst = Redis(password=secret, host=host, port=port, database_number=2)
