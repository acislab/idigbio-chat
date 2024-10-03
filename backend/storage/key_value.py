import redis
from threading import Thread
from fakeredis import TcpFakeServer


class FakeRedis:
    """
    Starts a fake redis server on a random open port. The port must be dynamic to avoid collisions when the flask app
    is hot-reloaded in debug environments.
    """
    __instance = None

    def __init__(self):
        # For debug mode, close the old store on reload
        if FakeRedis.__instance is not None:
            FakeRedis.__instance.close()
        FakeRedis.__instance = self

        self.server = TcpFakeServer(("localhost", 0,))
        t = Thread(target=self.server.serve_forever, daemon=True)
        t.start()

        host, port = self.server.server_address
        self.redis = redis.Redis(host=host, port=port)

    def close(self):
        self.redis.close()
        self.server.shutdown()

    def __getitem__(self, key):
        if isinstance(key, dict):
            return self.redis.get(str(key))

    def __setitem__(self, key, value):
        self.redis.hset(str(key), value)

    def __contains__(self, key):
        return self.redis.get(str(key)) is not None
