__version__: str
__version_tuple__: tuple[int|str, ...]
try:
    from tabulk._version import __version__, __version_tuple__ # type: ignore (only exist after creation of package)
except ModuleNotFoundError:
    __version__ = '0.0.0.dev0'
    __version_tuple__ = (0, 0, 0, 'dev0')
