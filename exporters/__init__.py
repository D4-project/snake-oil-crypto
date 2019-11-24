from importlib import import_module
from importlib import resources
import configparser

EXPORTERS = dict()

def register_exporter(func):
    """Decorator to register exporters"""
    name = func.__name__
    EXPORTERS[name] = func
    return func

def __getattr__(name):
    """Return a named exporters"""
    try:
        return EXPORTERS[name]
    except KeyError:
        _import_exporters()
        if name in EXPORTERS:
            return EXPORTERS[name]
        else:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            ) from None

def __dir__():
    """List available exporters"""
    _import_exporters()
    return list(EXPORTERS.keys())

def _import_exporters():
    """Import all resources to register exporters"""
    for name in resources.contents(__name__):
        if name.endswith(".py"):
            import_module(f"{__name__}.{name[:-3]}")

class Exporter:
    def __init__(self):
        """ Parse Config files """
        self.name = "default exporter"
        for name in resources.contents(__name__):
            if name == type(self).__name__ + ".conf":
                self.config = configparser.ConfigParser()
                self.config.read('exporters/'+name)

    def process(self):
        print("Default exporter doing nothing.")
