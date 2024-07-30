import redis
from rq import Queue

redis_connection = redis.Redis(host='localhost',
                               port=6379,
                               decode_responses=True)

global message_queue
message_queue = Queue(connection=redis_connection)
