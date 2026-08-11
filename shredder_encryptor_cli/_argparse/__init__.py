"""A small argparse extension that adds colour, grouped help and sub-commands.

The module is intentionally tiny: it only layers a few opinionated
defaults on top of :mod:`argparse` so the resulting command-line tool
looks polished without dragging in third-party dependencies.

The two public names are:

* :class:`ColorfulArgumentParser` -- drop-in replacement for
  :class:`argparse.ArgumentParser` that colours ``--help`` output,
  groups arguments visually and lets sub-parsers stay terse.
* :func:`style` -- convenience helper that wraps :mod:`color_code`
  and respects the ``NO_COLOR`` convention.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from .. import color_code as _cc

__all__ = ["ColorfulArgumentParser", "style", "add_common_arguments"]


# ---------------------------------------------------------------------------
# Colour handling
# ---------------------------------------------------------------------------
def _windows_enable_vt() -> bool:
    """Enable virtual terminal processing on the Windows console."""

    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)) == 0:
            return False
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        return bool(
            kernel32.SetConsoleMode(
                handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            )
        )
    except Exception:  # pragma: no cover - defensive
        return False


def _should_color(stream: Any) -> bool:
    """Return ``True`` when ``stream`` supports ANSI escapes."""

    if os.environ.get("NO_COLOR"):
        return False
    force = os.environ.get("SHREEDER_COLOR", "").lower()
    if force == "never":
        return False
    if force == "always":
        return True
    if not hasattr(stream, "isatty") or not stream.isatty():
        return False
    return _windows_enable_vt()


_COLOR_ENABLED: bool | None = None


def _colour_enabled() -> bool:
    """Memoised answer to ``_should_color(sys.stdout)``."""

    global _COLOR_ENABLED
    if _COLOR_ENABLED is None:
        _COLOR_ENABLED = _should_color(sys.stdout)
    return _COLOR_ENABLED


def style(text: str, *codes: str) -> str:
    """Wrap ``text`` in the given ANSI codes (no-op when not a TTY)."""

    if not _colour_enabled() or not codes:
        return text
    return "".join(codes) + text + _cc.ANSIColors.RESET


def shutil_get_terminal_width() -> int:
    """Return the terminal width, falling back to 100 when unavailable."""

    try:
        import shutil

        columns = shutil.get_terminal_size((100, 20)).columns
        return max(60, min(columns, 120))
    except Exception:  # pragma: no cover - defensive
        return 100


# ---------------------------------------------------------------------------
# Help formatter
# ---------------------------------------------------------------------------
class _ColorfulHelpFormatter(argparse.RawTextHelpFormatter):
    """Help formatter that colours section titles and ``--option`` text."""

    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 28,
        width: int | None = None,
    ) -> None:
        if width is None:
            width = shutil_get_terminal_width()
        super().__init__(prog, indent_increment, max_help_position, width)

    def start_section(self, text: str) -> None:  # type: ignore[override]
        if text:
            text = style(text, _cc.ANSIColors.BOLD, _cc.ANSIColors.CYAN)
        super().start_section(text)

    def _format_action_invocation(self, action: argparse.Action) -> str:
        if not action.option_strings:
            return super()._format_action_invocation(action)
        parts = list(action.option_strings)
        if action.nargs != 0 and action.dest != argparse.SUPPRESS:
            parts.append(style(action.dest.upper(), _cc.ANSIColors.YELLOW))
        return ", ".join(style(p, _cc.ANSIColors.GREEN) for p in parts)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------
class ColorfulArgumentParser(argparse.ArgumentParser):
    """Drop-in :class:`argparse.ArgumentParser` replacement with colour."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("formatter_class", _ColorfulHelpFormatter)
        kwargs.setdefault("exit_on_error", True)
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> None:  # type: ignore[override]
        sys.stderr.write(
            style("error:", _cc.ANSIColors.BOLD, _cc.ANSIColors.RED) + f" {message}\n"
        )
        self.exit(
            2,
            f"{style('Try', _cc.ANSIColors.BOLD)} '{self.prog} --help' for usage.\n",
        )

    def print_help(self, file: Any = None) -> None:  # type: ignore[override]
        if file is None:
            file = sys.stdout
        super().print_help(file)
        if _colour_enabled():
            file.write(
                "\n"
                + style("Tip:", _cc.ANSIColors.BOLD, _cc.ANSIColors.YELLOW)
                + " set "
                + style("NO_COLOR=1", _cc.ANSIColors.GREEN)
                + " to disable colours.\n"
            )

    def add_subparsers(self, **kwargs: Any) -> argparse._SubParsersAction:
        kwargs.setdefault("title", "commands")
        kwargs.setdefault(
            "metavar", style("<command>", _cc.ANSIColors.YELLOW, _cc.ANSIColors.BOLD)
        )
        kwargs.setdefault("help", "Pick one of the available commands.")
        return super().add_subparsers(**kwargs)


def add_common_arguments(
    parser: argparse.ArgumentParser,
    *,
    with_input: bool = True,
    with_output: bool = True,
) -> None:
    """Attach ``--input``/``--output`` arguments shared by every command."""

    if with_input:
        parser.add_argument(
            "-i",
            "--input",
            metavar="FILE",
            default="-",
            help="Read from FILE ('-' for stdin).",
        )
    if with_output:
        parser.add_argument(
            "-o",
            "--output",
            metavar="FILE",
            default="-",
            help="Write to FILE ('-' for stdout).",
        )
