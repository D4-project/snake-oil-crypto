from importlib import import_module
from importlib import resources
import configparser

BUILDERS = dict()

def register_builder(func):
    """Decorator to register builders"""
    name = func.__name__
    BUILDERS[name] = func
    return func

def __getattr__(name):
    """Return a named builders"""
    try:
        return BUILDERS[name]
    except KeyError:
        _import_builders()
        if name in BUILDERS:
            return BUILDERS[name]
        else:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            ) from None

def __dir__():
    """List available builders"""
    _import_builders()
    return list(BUILDERS.keys())


def _import_builders():
    """Import all resources to register builders"""
    for name in resources.contents(__name__):
        if name.endswith(".py"):
            import_module(f"{__name__}.{name[:-3]}")


class Builder:
    # def __init__(self):
    def __init__(self):
        """ Parse Config files """
        self.name = "default builder"
        for name in resources.contents(__name__):
            if name == type(self).__name__ + ".conf":
                self.config = configparser.ConfigParser()
                self.config.read('builders/'+name)


    def process(self):
        print("Default builder doing nothing.")
