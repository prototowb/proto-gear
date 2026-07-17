"""``python -m proto_gear_pkg`` entry point.

Mirrors the installed ``pg`` console script (``proto_gear_pkg.proto_gear:main``)
so the package is runnable without relying on the script being on ``PATH`` — the
interactive shell uses this to spawn real subcommands (init, sync-context,
hooks) at full fidelity.
"""

from .cli import main

if __name__ == "__main__":
    main()
