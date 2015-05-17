from jsl import BooleanField, Document, IntField


class Request(Document):

    project_id = IntField(minimum=0, required=True)
    archived = BooleanField()
    include_stories = BooleanField()


request = Request.get_schema()
response = None
