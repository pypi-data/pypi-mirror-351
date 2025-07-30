# src/opttech/core.py
"""
Camada central da OptTech.

Exemplo de uso
--------------
>>> from opttech.core import ler_arquivo_opttech
>>> dados = ler_arquivo_opttech("caminho/para/arquivo.opt")
"""

from pathlib import Path
from typing import Any, Dict

from .arquivos import map_files

__all__ = ["map_files"]
