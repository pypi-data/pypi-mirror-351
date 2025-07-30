from importlib.metadata import version, PackageNotFoundError
from .arquivos import map_files

__all__ = ["map_files"]


try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pacote não instalado (p. ex. durante CI checkout)
    __version__ = "0.0.0.dev0"