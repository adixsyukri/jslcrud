import jsl

from jslcrud.storage.memorystorage import MemoryStorage
import jslcrud.signals as signals
from common import get_client, run_jslcrud_test, PageCollection, PageModel
from common import ObjectCollection, ObjectModel
from common import NamedObjectCollection, NamedObjectModel
from common import App as BaseApp
from more.transaction import TransactionApp
from more.basicauth import BasicAuthIdentityPolicy


class App(BaseApp):
    pass


@App.identity_policy()
def get_identity_policy():
    return BasicAuthIdentityPolicy()


@App.verify_identity()
def verify_identity(identity):
    if identity.userid == 'admin' and identity.password == 'admin':
        return True
    return False


class PageStorage(MemoryStorage):
    model = PageModel


@App.path(model=PageCollection, path='pages')
def collection_factory(request):
    storage = PageStorage(request)
    return PageCollection(request, storage)


@App.path(model=PageModel, path='pages/{identifier}')
def model_factory(request, identifier):
    storage = PageStorage(request)
    return storage.get(identifier)


class ObjectStorage(MemoryStorage):
    incremental_id = True
    model = ObjectModel


@App.path(model=ObjectCollection, path='objects')
def object_collection_factory(request):
    storage = ObjectStorage(request)
    return ObjectCollection(request, storage)


@App.path(model=ObjectModel, path='objects/{identifier}')
def object_model_factory(request, identifier):
    storage = ObjectStorage(request)
    return storage.get(identifier)


class NamedObjectStorage(MemoryStorage):
    model = NamedObjectModel


@App.path(model=NamedObjectCollection, path='named_objects')
def namedobject_collection_factory(request):
    storage = NamedObjectStorage(request)
    return NamedObjectCollection(request, storage)


@App.path(model=NamedObjectModel, path='named_objects/{identifier}')
def namedobject_model_factory(request, identifier):
    storage = NamedObjectStorage(request)
    o = storage.get(identifier)
    return o


def test_memorystorage():
    run_jslcrud_test(App)
