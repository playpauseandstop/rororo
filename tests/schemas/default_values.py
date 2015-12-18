from jsl import (
    BooleanField,
    DictField,
    Document,
    IntField,
    StringField,
    UriField,
)


class Request(Document):

    include_data_id = StringField(default='0', enum=('0', '1'))


class Response(Document):

    data = DictField({
        'name': StringField(min_length=2, required=True),
        'url': UriField(),
        'main': BooleanField(default=False),
    }, required=True)
    data_id = IntField()
    system = StringField(default='dev')


request = Request.get_schema()
response = Response.get_schema()
