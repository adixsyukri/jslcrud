import jsl
from ..storage.sqlstorage import Base, GUID, SQLStorage
from .dictprovider import DictProvider
from ..app import App
from .base import Provider
import sqlalchemy as sa
from dateutil.parser import parse as parse_date
import uuid
from ..types import datestr
_MARKER = []


class SQLAlchemyModelProvider(Provider):

    def __init__(self, schema, data, storage):
        self.schema = schema
        self.data = data
        self.orm_model = data.__class__
        self.columns = self.orm_model.__table__.c
        self.storage = storage
        self.changed = False

    def __getitem__(self, key):
        if isinstance(self.columns[key].type, sa.DateTime):
            try:
                data = getattr(self.data, key)
            except AttributeError:
                raise KeyError(key)
            if data:
                return datestr(data.isoformat())
            return None
        if isinstance(self.columns[key].type, GUID):
            try:
                data = getattr(self.data, key)
            except AttributeError:
                raise KeyError(key)
            if data:
                return data.hex
            return None

        try:
            return getattr(self.data, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if key not in self.columns:
            return
        if value and isinstance(self.columns[key].type, sa.DateTime):
            value = parse_date(value)
        elif value and isinstance(self.columns[key].type, GUID):
            value = uuid.UUID(value)

        setattr(self.data, key, value)

    def __delitem__(self, key):
        setattr(self.data, key, None)

    def setdefault(self, key, value):
        if self.get(key):
            return
        self.set(key, value)

    def get(self, key, default=_MARKER):
        if default is _MARKER:
            attr = getattr(self.schema, key, None)
            if attr:
                if isinstance(attr, jsl.DocumentField):
                    default = []
                else:
                    default = getattr(self.schema, key).get_default()

        if default is not _MARKER:
            try:
                return self[key]
            except KeyError:
                return default
        return self[key]

    def set(self, key, value):
        self[key] = value

    def items(self):
        res = []
        fields = self.schema._fields.keys()
        for f in fields:
            res.append((f, self.data[f]))
        return res

    def keys(self):
        return self.schema._fields.keys()


@App.jslcrud_dataprovider(schema=jsl.Document, obj=Base, storage=SQLStorage)
def get_provider(schema, obj, storage):
    return SQLAlchemyModelProvider(schema, obj, storage)


@App.jslcrud_dataprovider(schema=jsl.Document, obj=dict, storage=SQLStorage)
def get_dict_provider(schema, obj, storage):
    return DictProvider(schema, obj, storage)


@App.jslcrud_jsonprovider(obj=SQLAlchemyModelProvider)
def get_jsonprovider(obj):
    fields = obj.schema._fields.items()
    result = {}
    for n, f in fields:
        v = obj.get(n)
        if v is None and not f.required:
            continue
        result[n] = v
    return result
