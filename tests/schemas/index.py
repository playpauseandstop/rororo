from jsl import Document, NumberField, StringField


NAME_ENUM = ('Igor', 'world')


class Request(Document):

    name = StringField(enum=NAME_ENUM, required=True)


class Response(Request):

    time = NumberField(required=True)


request = Request.get_schema()
response = Response.get_schema()
