import uuid

import attr
from aiohttp import web
from yarl import URL

from rororo.annotations import DictStrStr, TypedDict
from rororo.utils import to_bool


class TodoAPIDict(TypedDict):
    uid: str
    title: str
    order: int
    url: str
    completed: bool


@attr.dataclass
class Todo:
    title: str

    uid: uuid.UUID = attr.Factory(uuid.uuid4)
    order: int = 0
    completed: bool = False

    @classmethod
    def from_storage(cls, data: DictStrStr, *, uid: uuid.UUID) -> "Todo":
        """
        Create a storage object from a dict.

        Args:
            cls: (todo): write your description
            data: (todo): write your description
            uid: (str): write your description
            uuid: (str): write your description
            UUID: (str): write your description
        """
        return cls(
            uid=uid,
            title=data["title"],
            order=int(data["order"]),
            completed=to_bool(data["completed"]),
        )

    def get_absolute_url(self, *, request: web.Request) -> URL:
        """
        Returns the absolute url for the given request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            web: (str): write your description
            Request: (todo): write your description
        """
        return request.url.with_path(
            str(request.app.router["todo.get"].url_for(todo_uid=str(self.uid)))
        )

    def to_api_dict(self, *, request: web.Request) -> TodoAPIDict:
        """
        Returns a dict representation of the api.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            web: (todo): write your description
            Request: (todo): write your description
        """
        return {
            "uid": str(self.uid),
            "title": self.title,
            "order": self.order,
            "url": str(self.get_absolute_url(request=request)),
            "completed": self.completed,
        }

    def to_storage(self) -> DictStrStr:
        """
        Convert the object to a dict.

        Args:
            self: (todo): write your description
        """
        return {
            "title": self.title,
            "order": str(self.order),
            "completed": str(int(self.completed)),
        }
