import redis
from typing import Dict, Any

class Redis:
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.host = tool_config.get("host", "localhost")
        self.port = tool_config.get("port", 6379)
        self.db = tool_config.get("db", 0)
        self.password = tool_config.get("password")  # optional

        self.config = {
            "host": self.host,
            "port": self.port,
            "db": self.db
        }
        if self.password:
            self.config["password"] = self.password

        self.redis = None
        self.connect()

    def connect(self):
        try:
            self.redis = redis.StrictRedis(**self.config)
            # test connection
            self.redis.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def set(self, key: str, value: Any, cache_ttl: int = 86400) -> bool:
        """
        Sets a key with an optional TTL (in seconds).
        """
        return self.redis.set(key, value, ex=cache_ttl)

    def get(self, key: str) -> Any:
        return self.redis.get(key)

    def delete(self, key: str) -> int:
        return self.redis.delete(key)

    def read(self, query: str) -> Any:
        if query == "dbsize":
            return self.redis.dbsize()
        else:
            raise ValueError(f"Unsupported Redis query: {query}")

    def exists(self, key: str) -> bool:
        return self.redis.exists(key)
    
    def zadd(self, key: str, score: float, value: Any) -> int:
        return self.redis.zadd(key, score, value)
    
    def zrevrange(self, key: str, start: int, end: int, withscores: bool = False) -> list:
        return self.redis.zrevrange(key, start, end, withscores)
    
    
