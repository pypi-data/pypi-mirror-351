import typing
from typing import Any, Dict, Optional, Union, Type
from good_common.utilities import try_chain
from fast_depends import inject
from ._client import Redis, RedisProvider
from loguru import logger
import redis.exceptions

# The convert value function remains the same
_convert_value = try_chain(
    [
        lambda value: int(value),
        lambda value: float(value),
        lambda value: value.decode(),
        lambda value: value,
    ]
)


class DictProxy:
    """
    A dictionary-like interface to data stored in Redis with fallback to in-memory storage.
    """

    _instances: Dict[str, "DictProxy"] = {}

    def __new__(cls, name: str, *args, **kwargs):
        """
        Singleton pattern implementation to ensure one instance per name.
        """
        if name not in cls._instances:
            cls._instances[name] = super().__new__(cls)
        return cls._instances[name]

    @inject
    def __init__(
        self,
        name: str,
        expires: int = 60 * 60 * 24,  # 24 hours default
        default_object: Optional[Dict[str, Any]] = None,
        redis: Redis = RedisProvider(),
    ):
        # Skip re-initialization if already initialized
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._name = name
        self._expires = expires
        self._redis = redis
        self._redis_available = True
        self._fallback_storage: Dict[str, Any] = {}
        self._initialized = True

        # Initialize default values
        self._keys_and_defaults = default_object or {}

        # Add class annotations as defaults
        for key, type_hint in self.__class__.__annotations__.items():
            if key in self.__class__.__dict__:
                self._keys_and_defaults[key] = self.__class__.__dict__[key]

        # Collect property methods
        self._methods = {
            key
            for key, value in self.__class__.__dict__.items()
            if not key.startswith("_") and isinstance(value, property)
        }

        # Perform a Redis ping to check availability
        self._check_redis_connection()

    def _check_redis_connection(self) -> bool:
        """Check if Redis is available and update the status."""
        try:
            self._redis.ping()
            self._redis_available = True
            return True
        except (
            redis.exceptions.ConnectionError,
            redis.exceptions.TimeoutError,
            AttributeError,
            Exception,
        ) as e:
            logger.warning(
                f"Redis connection failed: {str(e)}. Using in-memory fallback."
            )
            self._redis_available = False
            return False

    def __getitem__(self, key: str) -> Any:
        """Get an item from Redis or fallback storage if Redis is unavailable."""
        if key not in self._keys_and_defaults:
            raise KeyError(f"Key {key} not found in defaults")

        # Try to get from Redis first if available
        if self._redis_available:
            try:
                val = self._redis.hget(self._name, key)
                if val is not None:
                    return _convert_value(val)
            except Exception as e:
                logger.warning(
                    f"Redis get error: {str(e)}. Falling back to in-memory storage."
                )
                self._redis_available = False  # Mark Redis as unavailable

        # Check fallback storage
        if key in self._fallback_storage:
            return self._fallback_storage[key]

        # Return default value
        return self._keys_and_defaults.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an item in Redis and fallback storage."""
        # Always update the fallback storage regardless of Redis status
        self._fallback_storage[key] = value

        # Try to update Redis if available
        if self._redis_available:
            try:
                self._redis.hset(self._name, key, value)
                self._redis.expire(self._name, self._expires)
            except Exception as e:
                logger.warning(
                    f"Redis set error: {str(e)}. Using in-memory storage only."
                )
                self._redis_available = False  # Mark Redis as unavailable

    def __getattribute__(self, name: str) -> Any:
        """
        Get attribute or item if not a private attribute or method.
        """
        # First check if this is a private attribute or a known method
        try:
            # Check if this is a special attribute or method
            if name.startswith("_") or (
                hasattr(self, "_methods") and name in self._methods
            ):
                return super().__getattribute__(name)
        except AttributeError:
            # During initialization, _methods might not exist yet
            if name.startswith("_"):
                return super().__getattribute__(name)

        # Otherwise treat it as a dictionary access
        return self[name]

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set attribute or item if not a private attribute.
        """
        if name.startswith("_"):
            return super().__setattr__(name, value)
        self[name] = value

    def force_redis_refresh(self) -> bool:
        """
        Force a check of the Redis connection and sync in-memory data to Redis if it's available.
        Returns whether Redis is available.
        """
        if self._check_redis_connection() and self._redis_available:
            # Sync all fallback storage to Redis
            for key, value in self._fallback_storage.items():
                try:
                    self._redis.hset(self._name, key, value)
                except Exception as e:
                    logger.error(f"Failed to sync key {key} to Redis: {str(e)}")
                    self._redis_available = False
                    return False

            # Set expiration
            try:
                self._redis.expire(self._name, self._expires)
            except Exception as e:
                logger.error(f"Failed to set expiration in Redis: {str(e)}")
                self._redis_available = False
                return False

            return True
        return False

    @property
    def __dict__(self) -> Dict[str, Any]:
        """
        Get all key-values as a dictionary, preferring Redis if available.
        """
        result = {}

        # Start with fallback storage
        result.update(self._fallback_storage)

        # Try to update with Redis data if available
        if self._redis_available:
            try:
                redis_data = self._redis.hgetall(self._name)
                redis_dict = {
                    k.decode() if isinstance(k, bytes) else k: _convert_value(v)
                    for k, v in redis_data.items()
                }
                result.update(redis_dict)
            except Exception as e:
                logger.warning(f"Failed to get all items from Redis: {str(e)}")
                self._redis_available = False

        return result

    def __repr__(self) -> str:
        """String representation of the object."""
        data = self.__dict__
        storage_type = "Redis" if self._redis_available else "fallback"
        return f"<{self.__class__.__name__} {self._name} using {storage_type} storage: {data}>"


# import typing
# from good_common.utilities import try_chain
# from fast_depends import inject
# from ._client import Redis, RedisProvider
# from loguru import logger

# _convert_value = try_chain(
#     [
#         lambda value: int(value),
#         lambda value: float(value),
#         lambda value: value.decode(),
#         lambda value: value,
#     ]
# )


# class DictProxy:
#     @inject
#     def __init__(
#         self,
#         name: str,
#         expires: int = 60 * 60 * 24,
#         default_object: dict | None = None,
#         redis: Redis = RedisProvider(),
#     ):
#         self._name = name
#         self._expires = expires
#         self._redis = redis

#         self._keys_and_defaults = default_object or {}

#         for key in self.__class__.__annotations__.keys():
#             self._keys_and_defaults[key] = self.__class__.__dict__[key]

#         self._methods = set()

#         for key in self.__class__.__dict__.keys():
#             if not key.startswith("_") and isinstance(
#                 self.__class__.__dict__[key], property
#             ):
#                 self._methods.add(key)

#     def __getitem__(self, key):
#         if key not in self._keys_and_defaults:
#             raise KeyError(f"Key {key} not found in defaults")
#         if (val := self._redis.hget(self._name, key)) is not None:
#             return _convert_value(val)
#         return self._keys_and_defaults.get(key)

#     def __setitem__(self, key, value):
#         # logger.debug(f"Setting {self._name}.{key} to {value}")
#         self._redis.hset(self._name, key, value)
#         self._redis.expire(self._name, self._expires)

#     def __getattribute__(self, name: str) -> typing.Any:
#         if name.startswith("_") or name in self._methods:
#             return super().__getattribute__(name)
#         return self[name]

#     def __setattr__(self, name: str, value: typing.Any) -> None:
#         if name.startswith("_"):
#             return super().__setattr__(name, value)
#         self[name] = value

#     @property
#     def __dict__(self):
#         return {
#             k.decode(): _convert_value(v)
#             for k, v in self._redis.hgetall(self._name).items()
#         }

#     def __repr__(self):
#         return f"<{self.__class__.__name__} {self._name} {self.__dict__}>"
