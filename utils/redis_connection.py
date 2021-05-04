import redis

from my_settings import REDIS_PORT, REDIS_HOST


class RedisConnection(object):
    def __init__(self):
        self.conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
