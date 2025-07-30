"""
connexity_pipecat
~~~~~~~~~~
Python toolkit for building voice agents.
"""

from importlib.metadata import version as _pkg_version

# Public-facing helpers you want users to do
#   >>> from connexity_pipecat import init_config, register_routes
from connexity_pipecat.core.config import init_config
from connexity_pipecat.core.generators.management import register_custom_generators
from connexity_pipecat.core.tools.management import register_custom_tools
from connexity_pipecat.api.router import register_routes, register_custom_handlers

__all__ = [
    "init_config",
    "register_custom_tools",
    "register_routes",
    "register_custom_handlers",
    "register_custom_generators"
]

# --------------------------------------------------------------------------- #
# Package version                                                             #
# --------------------------------------------------------------------------- #

try:
    __version__: str = _pkg_version("agent-zero")
except Exception:  # pragma: no cover
    # Editable install or unpackaged source tree
    __version__ = "0.0.0"