import importlib
from os import path
from typing import TYPE_CHECKING

import hcs_core.ctxp as _ctxp
from hcs_core.sglib.client_util import hdc_service_client as client

config_path = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "config"))
_ctxp.init("hcs", config_path=config_path)

# Define submodules in a single place
__submodules = sorted(
    [
        "admin",
        "app_management",
        "auth",
        "av",
        "clouddriver",
        "credential",
        "hoc",
        "ims",
        "inventory",
        "iss",
        "lcm",
        "org_service",
        "pki",
        "portal",
        "scm",
        "synt",
        "tsctl",
        "vmhub",
        "vmm",
        "csp",
        "graphql",
        "pool",
        "task",
        "template",
    ]
)

# Map submodule names to their full import paths
__submodule_map = {name: f"hcs_cli.service.{name}" for name in __submodules}

# Optional: for type-checking and IDE autocompletion
if TYPE_CHECKING:
    from . import admin  # type: ignore
    from . import app_management  # type: ignore
    from . import auth  # type: ignore
    from . import av  # type: ignore
    from . import clouddriver  # type: ignore
    from . import credential  # type: ignore
    from . import csp  # type: ignore
    from . import graphql  # type: ignore
    from . import hoc  # type: ignore
    from . import lcm  # type: ignore
    from . import org_service  # type: ignore
    from . import pki  # type: ignore
    from . import pool  # type: ignore
    from . import portal  # type: ignore
    from . import scm  # type: ignore
    from . import synt  # type: ignore
    from . import task  # type: ignore
    from . import tsctl  # type: ignore
    from . import vmhub  # type: ignore
    from . import vmm  # type: ignore

# Specify the submodules to load lazily


def __getattr__(name):
    if name in __submodule_map:
        # Dynamically import the submodule
        submodule = importlib.import_module(__submodule_map[name])
        # Cache the imported module in the package's namespace
        globals()[name] = submodule
        return submodule
    raise AttributeError(f"Module {__name__!r} has no attribute {name!r}")


# Optional: __all__ for explicit exports
__all__ = ["client"] + __submodules


def __dir__():
    # Add lazy submodules to the directory listing
    return __all__
