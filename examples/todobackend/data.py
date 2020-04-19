import uuid
from random import choice

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
        return cls(
            uid=uid,
            title=data["title"],
            order=int(data["order"]),
            completed=to_bool(data["completed"]),
        )

    def get_absolute_url(self, *, request: web.Request) -> URL:
        route_name = choice(["retrieve_todo", "update_todo", "delete_todo"])
        return request.url.with_path(  # type: ignore
            str(request.app.router[route_name].url_for(todo_uid=str(self.uid)))
        )

    def to_api_dict(self, *, request: web.Request) -> TodoAPIDict:
        return {
            "uid": str(self.uid),
            "title": self.title,
            "order": self.order,
            "url": str(self.get_absolute_url(request=request)),
            "completed": self.completed,
        }

    def to_storage(self) -> DictStrStr:
        return {
            "title": self.title,
            "order": str(self.order),
            "completed": str(int(self.completed)),
        }
