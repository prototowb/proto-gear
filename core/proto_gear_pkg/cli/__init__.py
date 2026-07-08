"""Command-line interface layer for Proto Gear.

Top layer of the target module architecture (see ADR-001): argparse
construction (:mod:`~proto_gear_pkg.cli.parser`) and command dispatch
(:mod:`~proto_gear_pkg.cli.app`) only. No business logic — that lives in the
engine (``proto_gear.py``) and the module-core / module packages.
"""

from .app import main

__all__ = ["main"]
