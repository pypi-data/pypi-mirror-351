try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # Compatível com Python <3.8

__version__ = version("fk7py")

from .FK7Python import FK7