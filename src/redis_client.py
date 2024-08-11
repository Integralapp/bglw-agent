import redis
from rq import Queue
import sys


def print_message_id(messageId):
    print(messageId)


class RedisClient:
    _connection = None

    @staticmethod
    def get_queue():
        if RedisClient._connection is None:
            # Initialize the Redis connection if it doesn't exist
            RedisClient._connection = redis.Redis(host='localhost',
                                                  port=6379,
                                                  db=0)
        return Queue(connection=RedisClient._connection)

    @staticmethod
    def enqueue(messageId):
        RedisClient.get_queue().enqueue(print_message_id, messageId)
