from ..errors import NotFoundError
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from rulez import compile_condition
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid


class SQLStorage(object):

    _temp = {}

    @property
    def model(self):
        raise NotImplementedError

    @property
    def orm_model(self):
        raise NotImplementedError

    def set_identifier(self, obj, identifier):
        for f, v in zip(
                self.app.get_jslcrud_identifierfields(self.model.schema),
                identifier.split(
                    self.app.get_jslcrud_compositekey_separator())):
            obj[f] = v

    def __init__(self, request):
        self.request = request
        self.app = request.app

    @property
    def session(self):
        return self.request.db_session

    def create(self, data):
        values = data
        o = self.orm_model()
        data = {}
        for fieldname, field in self.model.schema._fields.items():
            if field.required:
                data[fieldname] = field.get_default()
        data.update(values)
        dst = self.app.get_jslcrud_dataprovider(self.model.schema, o)
        src = self.app.get_jslcrud_dataprovider(self.model.schema, data)
        for k, v in src.items():
            dst[k] = v
        m = self.model(self.request, self, o)
        identifier = m.identifier
        self.session.add(o)
        self.session.flush()
        self.session.refresh(o)
        return m

    def search(self, query=None, limit=None):
        if query:
            f = compile_condition('sqlalchemy', query)
            filterquery = f(self.orm_model)
            q = self.session.query(self.orm_model).filter(filterquery)
        else:
            q = self.session.query(self.orm_model)
        if limit is not None:
            q = q.limit(limit)

        return [self.model(self.request, self, o) for o in q.all()]

    def get(self, identifier):
        qs = []
        for f, v in zip(
                self.app.get_jslcrud_identifierfields(self.model.schema),
                identifier.split(self.app.get_jslcrud_compositekey_separator())):
            qs.append(getattr(self.orm_model, f) == v)
        q = self.session.query(self.orm_model).filter(sa.and_(*qs))
        r = q.first()
        if not r:
            raise NotFoundError(self.model, identifier)
        return self.model(self.request, self, r)

    def get_by_uuid(self, uuid):
        uuid_field = self.app.get_jslcrud_uuidfield(self.model.schema)
        if getattr(self.orm_model, uuid_field, None) is None:
            raise AttributeError('%s does not have %s field' %
                                 (self.orm_model, uuid_field))
        qs = getattr(self.orm_model, uuid_field) == uuid
        q = self.session.query(self.orm_model).filter(qs)
        r = q.first()
        if not r:
            raise NotFoundError(self.model, uuid)
        return self.model(self.request, self, r)

    def update(self, identifier, data):
        qs = []
        for f, v in zip(
                self.app.get_jslcrud_identifierfields(self.model.schema),
                identifier.split(self.app.get_jslcrud_compositekey_separator())):
            qs.append(getattr(self.orm_model, f) == v)
        q = self.session.query(self.orm_model).filter(sa.and_(*qs))

        r = q.first()
        if not r:
            raise ValueError(identifier)

        d = self.app.get_jslcrud_dataprovider(self.model.schema, r)
        for k, v in data.items():
            d[k] = v

        return self.model(self.request, self, r)

    def delete(self, identifier):
        qs = []
        for f, v in zip(
                self.app.get_jslcrud_identifierfields(self.model.schema),
                identifier.split(self.app.get_jslcrud_compositekey_separator())):
            qs.append(getattr(self.orm_model, f) == v)
        q = self.session.query(self.orm_model).filter(sa.and_(*qs))

        r = q.first()
        if not r:
            raise ValueError(identifier)

        self.session.delete(r)


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class BaseMixin(object):

    uuid = sa.Column(GUID, primary_key=True, default=uuid.uuid4)
    created = sa.Column(sa.DateTime, default=datetime.utcnow)
    last_modified = sa.Column(sa.DateTime, default=datetime.utcnow)


Base = declarative_base(cls=BaseMixin)
