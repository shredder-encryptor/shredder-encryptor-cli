"""Sub-commands exposed by the ``shredder-cli`` entry point.

Each module in this package defines a :func:`add_parser` that wires a
single sub-command onto the top-level parser.  Commands stay small
so they are easy to read and to disable individually.
"""

from __future__ import annotations

from typing import Callable

#: Type alias for ``add_parser(parser)`` style registrations.
CommandFactory = Callable[[object], None]

__all__ = ["CommandFactory", "register_all"]


def register_all(parsers: object) -> None:
    """Attach every command in this package to ``parsers``."""

    # Imported lazily so that ``shredder_cli --help`` stays cheap even
    # when a dependency is missing.
    from . import cipher, encode, keystore

    encode.add_parser(parsers)
    cipher.add_parser(parsers)
    keystore.add_parser(parsers)
