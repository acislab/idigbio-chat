from expandvars import expandvars
from flask import Flask
from redis import Redis

from storage.fake_redis import FakeRedis


class FlaskRedis:
    inst: Redis

    def init_app(self, app: Flask):
        if "REDIS" not in app.config or not app.config["REDIS"].get("URI"):
            self.inst = FakeRedis().redis
            print("Using temporary Redis instance")
        else:
            uri = expandvars(app.config["REDIS"]["URI"])
            print(f"Connecting to Redis: {uri}")
            self.inst = Redis.from_url(uri)

        app.config["SESSION_REDIS"] = self.inst

        self.inst.ping()
