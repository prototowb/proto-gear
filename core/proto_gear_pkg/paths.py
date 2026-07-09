"""Locations of bundled package resources.

Modules live at varying depths (root, ``cli/``, ``module_core/``,
``modules/engineering/``), but the bundled data they read — capability
bundles, host templates, the ``modules/`` tree — lives at the package root.
Resolving those via ``Path(__file__).parent`` breaks the moment a module
changes depth; :func:`package_root` is the single, depth-independent anchor.
"""

from pathlib import Path


def package_root() -> Path:
    """Return the ``proto_gear_pkg`` package directory (bundled-resource root)."""
    return Path(__file__).parent
