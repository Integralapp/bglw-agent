import redis
from rq import Queue
from .google_service import GoogleService


def print_message_id(params):
    messageId = params['message_id']
    print(messageId)
    google_service = params['google_service']
    if google_service is None:
        raise Exception("Google Service None")

    message_details = google_service.users().messages().get(
        userId="me", id=messageId).execute()
    print(f"New message: {message_details['snippet']}")


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
    def enqueue(params):
        RedisClient.get_queue().enqueue(print_message_id, params)
