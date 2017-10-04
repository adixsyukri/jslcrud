from ..app import App
from .base import Provider
from ..types import datestr
from ..storage.memorystorage import MemoryStorage
import jsl


_MARKER = []


class DictProvider(Provider):

    def __init__(self, schema, data, storage):
        self.schema = schema
        self.data = data
        self.storage = storage

    def __getitem__(self, key):
        if isinstance(self.schema._fields[key], jsl.DateTimeField):
            return datestr(self.data[key])
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def setdefault(self, key, value):
        return self.data.setdefault(key, value)

    def get(self, key, default=_MARKER):
        if default is _MARKER:
            return self.data.get(key)
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()


@App.jslcrud_dataprovider(schema=jsl.Document, obj=dict, storage=MemoryStorage)
def get_dataprovider(schema, obj, storage):
    return DictProvider(schema, obj, storage)


@App.jslcrud_jsonprovider(obj=DictProvider)
def get_jsonprovider(obj):
    return obj.data
