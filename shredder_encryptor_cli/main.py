"""Top-level :func:`main` used by ``shredder-cli`` (and by the test suite)."""

from __future__ import annotations

import sys
from typing import Sequence

from ._argparse import ColorfulArgumentParser
from .commands import register_all
from .ui import info, success

__all__ = ["build_parser", "main"]


def build_parser() -> ColorfulArgumentParser:
    """Return the fully-configured CLI parser.

    Exposed so the test suite can drive the parser without going
    through :mod:`argparse`'s exit paths.
    """

    parser = ColorfulArgumentParser(
        prog="shredder-cli",
        description=(
            "Friendly command-line front-end for the shredder-encryptor package.\n"
            "Comes with colourful help, no third-party runtime dependencies."
        ),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the shredder-encryptor version and exit.",
    )
    sub = parser.add_subparsers(dest="command", required=False)
    register_all(sub)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI with ``argv`` (defaults to :data:`sys.argv[1:]`)."""

    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(list(argv))
    if args.version:
        from shredder_encryptor import __version__

        info(f"shredder-encryptor {__version__}")
        return 0
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0
    result = handler(args)
    if isinstance(result, int):
        return result
    success("done")
    return 0
