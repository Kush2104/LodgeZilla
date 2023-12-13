import os, redis
from utils import read_from_redis


REDIS_KEY = "toWorkers"
redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379
r = redis.StrictRedis(host=redisHost, port=redisPort, db=0)
read_from_redis(r, REDIS_KEY)