from ..errors import NotFoundError
from morepath.request import Request
from rulez import compile_condition
from .base import BaseStorage
import jsl

DATA = {}


class MemoryStorage(BaseStorage):

    incremental_id = False

    @property
    def datastore(self):
        return DATA[self.typekey]

    @property
    def typekey(self):
        return ':'.join([self.__module__, self.__class__.__name__])

    def __init__(self, request):
        DATA.setdefault(self.typekey, {})
        super(MemoryStorage, self).__init__(request)

    def create(self, data):
        data = data.copy()
        obj = self.model(self.request, self, data)
        if self.incremental_id:
            obj.data['id'] = len(DATA[self.typekey]) + 1
        identifier = obj.identifier
        DATA[self.typekey][identifier] = obj
        return obj

    def search(self, query=None, offset=None, limit=None, order_by=None):
        res = []
        if query:
            f = compile_condition('native', query)
            for o in DATA[self.typekey].values():
                if f(o.data):
                    res.append(o)
        else:
            res = list(DATA[self.typekey].values())
        for r in res:
            r.request = self.request
        if offset is not None:
            res = res[offset:]
        if limit is not None:
            res = res[:limit]
        if order_by is not None:
            col, d = order_by
            res = list(sorted(res, key=lambda x: x.data[col]))
            if d == 'desc':
                res = list(reversed(res))
        return res

    def get(self, identifier):
        if identifier not in DATA[self.typekey].keys():
            raise NotFoundError(self.model, identifier)
        res = DATA[self.typekey][identifier]
        res.request = self.request
        return res

    def get_by_uuid(self, uuid):
        uuid_field = self.app.get_jslcrud_uuidfield(self.model.schema)
        data_by_uuid = {}
        for u, v in DATA[self.typekey].items():
            if uuid_field not in v.data.keys():
                raise AttributeError(
                    '%s does not have %s field' % (v, uuid_field))
            data_by_uuid[v.data[uuid_field]] = v

        if uuid not in data_by_uuid.keys():
            raise NotFoundError(self.model, uuid)
        res = data_by_uuid[uuid]
        res.request = self.request
        return res

    def update(self, identifier, data):
        obj = DATA[self.typekey][identifier]
        for k, v in data.items():
            obj.data[k] = v
        return obj

    def delete(self, identifier):
        del DATA[self.typekey][identifier]
