"""
LuxorASAP – pacote principal.

Carrega subpacotes e expõe um ponto único de versão.
"""

from importlib.metadata import PackageNotFoundError, version as _pkg_version

try:
    __version__: str = _pkg_version(__name__)
except PackageNotFoundError:  # pacote ainda não instalado (editable during dev)
    __version__ = "0.0.0"

# Reexporta submódulos principais
from . import datareader, ingest, utils  # noqa: F401

# Conveniência opcional – permite:  from luxorasap import LuxorQuery
#from .datareader import LuxorQuery  # noqa: F401

__all__ = ["__version__", "datareader", "ingest", "utils", "LuxorQuery"]