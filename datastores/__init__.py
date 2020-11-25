from contextlib import ContextDecorator
from importlib import import_module
from importlib import resources
import configparser

DATASTORES = dict()

def register_datastore(func):
    """Decorator to register attacks"""
    name = func.__name__
    DATASTORES[name] = func
    return func

def __getattr__(name):
    """Return a named datastore"""
    try:
        return DATASTORES[name]
    except KeyError:
        _import_datastores()
        if name in DATASTORES:
            return DATASTORES[name]
        else:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            ) from None

def __dir__():
    """List available datastores"""
    _import_datastores()
    return list(DATASTORES.keys())

def _import_datastores():
    """Import all resources to register datastores"""
    for name in resources.contents(__name__):
        if name.endswith(".py"):
            import_module(f"{__name__}.{name[:-3]}")

class DataStore(ContextDecorator):
# class DataStore:
    """" Datastores can be used as decorators of as contexts. """
    def __init__(self):
        """ Parse Config files """
        self.name = "default datastore"
        for name in resources.contents(__name__):
            if name == type(self).__name__ + ".conf":
                self.config = configparser.ConfigParser()
                self.config.read('datastores/'+name)

    def __enter__(self):
        return self

    def __exit__(self ,exc_type, exc_value, tb):
        self.disconnect()
        if exc_type is not None:
            return False
        return True
