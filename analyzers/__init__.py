from importlib import import_module
from importlib import resources
import configparser
import pdb

ANALYZERS = dict()

def register_analyzer(func):
    """Decorator to register analyzers"""
    name = func.__name__
    ANALYZERS[name] = func
    return func

def __getattr__(name):
    """Return a named analyzers"""
    try:
        return ANALYZERS[name]
    except KeyError:
        _import_analyzers()
        if name in ANALYZERS:
            return ANALYZERS[name]
        else:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            ) from None

def __dir__():
    """List available analyzers"""
    _import_analyzers()
    return list(ANALYZERS.keys())

def _import_analyzers():
    """Import all resources to register analyzers"""
    for name in resources.contents(__name__):
        if name.endswith(".py"):
            import_module(f"{__name__}.{name[:-3]}")

class Analyzer:
    def __init__(self):
        """ Parse Config files """
        self.name = "default analyzer"
        for name in resources.contents(__name__):
            if name == type(self).__name__ + ".conf":
                self.config = configparser.ConfigParser()
                self.config.read('analyzers/'+name)

    def process(self):
        print("Default analyzer doing nothing.")
