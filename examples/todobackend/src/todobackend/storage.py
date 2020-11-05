import uuid
from typing import Optional, Union

import pyrsistent
from aioredis.connection import RedisConnection
from pyrsistent.typing import PVector

from .data import Todo


class Storage:
    def __init__(self, *, redis: RedisConnection, data_key: str) -> None:
        """
        Initialize a redis instance.

        Args:
            self: (todo): write your description
            redis: (todo): write your description
            data_key: (str): write your description
        """
        self.redis = redis
        self.data_key = data_key

    def build_item_key(self, mixed: Union[str, Todo, uuid.UUID]) -> str:
        """
        Build the key for the given item.

        Args:
            self: (todo): write your description
            mixed: (todo): write your description
        """
        uid = mixed.uid if isinstance(mixed, Todo) else mixed
        return ":".join((self.data_key, str(uid)))

    async def create_todo(self, todo: Todo) -> None:
          """
          Create a todotodoist.

          Args:
              self: (todo): write your description
              todo: (str): write your description
          """
        await self.redis.rpush(self.data_key, str(todo.uid))
        await self.save_todo(todo)

    async def delete_todo(self, todo: Todo) -> int:
          """
          Delete a todoist.

          Args:
              self: (todo): write your description
              todo: (str): write your description
          """
        redis = self.redis

        await redis.lrem(self.data_key, 0, str(todo.uid))
        return await redis.delete(self.build_item_key(todo))  # type: ignore

    async def delete_todos(self) -> int:
          """
          Removes all data from the cache.

          Args:
              self: (todo): write your description
          """
        redis = self.redis
        counter = 0

        for key in await redis.lrange(self.data_key, 0, -1):
            counter += await redis.delete(self.build_item_key(key))

        await redis.delete(self.data_key)
        return counter

    async def get_todo(self, uid: uuid.UUID) -> Optional[Todo]:
          """
          Get a todo item.

          Args:
              self: (todo): write your description
              uid: (str): write your description
              uuid: (todo): write your description
              UUID: (todo): write your description
          """
        data = await self.redis.hgetall(self.build_item_key(uid))
        if not data:
            return None
        return Todo.from_storage(data, uid=uid)

    async def list_todos(self) -> PVector[Todo]:
          """
          Returns a list of todoos.

          Args:
              self: (todo): write your description
          """
        redis = self.redis

        data = []
        for key in await redis.lrange(self.data_key, 0, -1):
            uid = uuid.UUID(key)
            item_key = self.build_item_key(uid)

            data.append(
                Todo.from_storage(await redis.hgetall(item_key), uid=uid)
            )

        return pyrsistent.v(*data)

    async def save_todo(self, todo: Todo) -> None:
          """
          Save a todoist.

          Args:
              self: (todo): write your description
              todo: (todo): write your description
          """
        await self.redis.hmset_dict(
            self.build_item_key(todo), todo.to_storage()
        )
