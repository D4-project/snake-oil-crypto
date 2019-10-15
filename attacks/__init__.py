from importlib import import_module
from importlib import resources

ATTACKS = dict()

def register_attack(func):
    """Decorator to register attacks"""
    name = func.__name__
    ATTACKS[name] = func
    return func

def __getattr__(name):
    """Return a named attacks"""
    try:
        return ATTACKS[name]
    except KeyError:
        _import_attacks()
        if name in ATTACKS:
            return ATTACKS[name]
        else:
            raise AttributeError(
                f"module {__name__!r} has no attribute {name!r}"
            ) from None

def __dir__():
    """List available attacks"""
    _import_attacks()
    return list(ATTACKS.keys())


def _import_attacks():
    """Import all resources to register attacks"""
    for name in resources.contents(__name__):
        if name.endswith(".py"):
            import_module(f"{__name__}.{name[:-3]}")


class Attack:
    # def __init__(self):
    def __init__(self):
        self.name = "default attack"

    def process(self):
        print("Default attack doing nothing.")
