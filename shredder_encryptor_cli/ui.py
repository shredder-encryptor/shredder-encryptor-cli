"""Small rendering helpers used by the command-line interface.

The functions wrap the low-level :func:`shredder_encryptor_cli._argparse.style`
helper so the rest of the CLI can stay short.  They never raise; an
IOError simply means the message was not delivered.
"""

from __future__ import annotations

import sys
from typing import TextIO

from . import color_code as _cc
from ._argparse import _colour_enabled, style

__all__ = ["info", "success", "warn", "error", "rule", "bullet"]


def _emit(stream: TextIO, icon: str, colour: str, message: str) -> None:
    """Print ``message`` with an icon and a colour to ``stream``."""

    enabled = _colour_enabled()
    if enabled:
        prefix = style(f"{icon} ", colour, _cc.ANSIColors.BOLD)
        body = style(message, colour)
    else:
        prefix = f"{icon} "
        body = message
    print(f"{prefix}{body}", file=stream)


def info(message: str, *, stream: TextIO = sys.stdout) -> None:
    """Print an informational message with a blue ``i`` icon."""

    _emit(stream, "i", _cc.ANSIColors.BLUE, message)


def success(message: str, *, stream: TextIO = sys.stdout) -> None:
    """Print a success message with a green check mark."""

    _emit(stream, "\u2713", _cc.ANSIColors.GREEN, message)


def warn(message: str, *, stream: TextIO = sys.stderr) -> None:
    """Print a warning with a yellow ``!`` icon."""

    _emit(stream, "!", _cc.ANSIColors.YELLOW, message)


def error(message: str, *, stream: TextIO = sys.stderr) -> None:
    """Print an error with a red cross."""

    _emit(stream, "\u2717", _cc.ANSIColors.RED, message)


def rule(title: str = "", *, stream: TextIO = sys.stdout) -> None:
    """Print a horizontal rule with an optional centred title."""

    enabled = _colour_enabled()
    width = 60
    if title:
        title_text = f" {title} "
        if enabled:
            title_text = style(title_text, _cc.ANSIColors.BOLD, _cc.ANSIColors.CYAN)
        pad = max(0, width - len(title))
        left = "-" * (pad // 2)
        right = "-" * (pad - pad // 2)
        line = f"{left}{title_text}{right}"
    else:
        line = f"{title}".center(width, "-")
    print(line, file=stream)


def bullet(items: list[str], *, stream: TextIO = sys.stdout) -> None:
    """Print ``items`` as a bulleted list."""

    for item in items:
        prefix = style("  - ", _cc.ANSIColors.GREEN) if _colour_enabled() else "  - "
        print(f"{prefix}{item}", file=stream)
