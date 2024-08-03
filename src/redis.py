import redis
from rq import Queue

class RedisConnection:
    _connection = None

    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db

    def start_connection(self):
        """Establish a connection to the Redis server."""
        if RedisConnection._connection is None:
            RedisConnection._connection = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=True)
        return RedisConnection._connection

    @classmethod
    def get_queue(cls):
        """Retrieve the existing Redis connection, or raise an error if not connected."""
        if cls._connection is None:
            raise ConnectionError("Redis connection has not been established. Please call start_connection() first.")
        return Queue(connection=cls._connection)


def main():
    # Create a RedisConnection instance
    redis_conn = RedisConnection(host='localhost', port=6379, db=0)

    # Start the connection
    redis_conn.start_connection()

if __name__ == "__main__":
    main()