import uuid

import attr
import pyrsistent
from todobackend.data import Todo
from todobackend.storage import Storage


async def test_storage(
    todobackend_data, todobackend_redis, todobackend_settings
):
      """
      Create a new data in storage.

      Args:
          todobackend_data: (todo): write your description
          todobackend_redis: (todo): write your description
          todobackend_settings: (str): write your description
      """
    settings = todobackend_settings()
    async with todobackend_redis(settings=settings) as redis:
        storage = Storage(redis=redis, data_key=settings.redis_data_key)

        assert await storage.list_todos() == []

        todo = Todo(title=todobackend_data["title"])
        await storage.create_todo(todo)
        assert await storage.list_todos() == pyrsistent.v(todo)
        assert await storage.get_todo(todo.uid) == todo

        completed_todo = attr.evolve(todo, completed=True)
        assert await storage.save_todo(completed_todo) != todo
        assert await storage.get_todo(todo.uid) == completed_todo

        assert await storage.delete_todo(todo) == 1
        assert await storage.get_todo(todo.uid) is None

        await storage.create_todo(todo)
        await storage.create_todo(
            attr.evolve(completed_todo, uid=uuid.uuid4())
        )
        assert await storage.delete_todos() == 2

        assert await storage.delete_todo(todo) == 0
        assert await storage.delete_todos() == 0
