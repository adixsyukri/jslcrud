from ..errors import NotFoundError
from morepath.request import Request
from rulez import compile_condition

DATA = {}


class MemoryStorage(object):

    incremental_id = False

    def set_identifier(self, obj, identifier):
        for f, v in zip(
                self.app.get_jslcrud_identifierfields(self.model.schema),
                identifier.split(
                    self.app.get_jslcrud_compositekey_separator())):
            obj[f] = v

    @property
    def datastore(self):
        return DATA[self.typekey]

    @property
    def model(self):
        raise NotImplementedError

    @property
    def typekey(self):
        return ':'.join([self.__module__, self.__class__.__name__])

    def __init__(self, request):
        DATA.setdefault(self.typekey, {})
        self.request = request
        self.app = request.app

    def create(self, data):
        data = data.copy()
        obj = self.model(self.request, self, data)
        if self.incremental_id:
            obj.data['id'] = len(DATA[self.typekey]) + 1
        identifier = obj.identifier
        DATA[self.typekey][identifier] = obj
        return obj

    def search(self, query=None, limit=None):
        res = []
        if query:
            f = compile_condition('native', query)
            for o in DATA[self.typekey].values():
                if f(o.data):
                    res.append(o)
        else:
            res = DATA[self.typekey].values()
        for r in res:
            r.request = self.request
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

    def get_json(self, identifier):
        obj = self.get(identifier)
        data = self.app.get_jslcrud_jsonprovider(obj.data)
        return data

    def update(self, identifier, data):
        obj = DATA[self.typekey][identifier]
        for k, v in data.items():
            obj.data[k] = v
        return obj

    def delete(self, identifier):
        del DATA[self.typekey][identifier]
