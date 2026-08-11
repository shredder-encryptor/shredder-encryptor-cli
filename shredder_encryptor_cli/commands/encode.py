"""``encode`` / ``decode`` sub-commands backed by :mod:`shredder_encryptor.codec`."""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Callable

from .._argparse import add_common_arguments, style
from .. import color_code as _cc
from ..ui import bullet, info, success

__all__ = ["add_parser", "ENCODINGS"]


#: Name of the codec package that supplies every encoder / decoder.
_CODEC_PACKAGE = "shredder_encryptor.codec"


def _submodule(name: str) -> object:
    """Return a codec submodule from :data:`_CODEC_PACKAGE`.

    This deliberately uses :func:`importlib.import_module` (which always
    returns the parent package, never a re-exported attribute) and then
    reaches for the requested submodule via :func:`getattr`.  The previous
    implementation used ``__import__(..., fromlist=[name])``, which has a
    well-known footgun: when ``fromlist`` names a submodule, ``__import__``
    returns *that* submodule rather than the parent package.  Combined with
    re-exports in :mod:`shredder_encryptor.codec.__init__` (e.g. ``uuencode``
    is both a submodule and a function), the call could resolve to a
    callable and the subsequent attribute access would explode with
    ``AttributeError`` at run time.
    """

    package = importlib.import_module(_CODEC_PACKAGE)
    module = getattr(package, name)
    if not hasattr(module, name):
        # ``getattr`` may pick up a re-exported symbol (function, class, ...)
        # that happens to share the submodule's name.  In that case fall
        # back to importing the submodule explicitly so attribute access
        # below always sees a real module object.
        module = importlib.import_module(f"{_CODEC_PACKAGE}.{name}")
    return module


#: Mapping from encoding name to its codec pair.  Each pair exposes
#: ``encode(bytes) -> bytes`` and ``decode(bytes) -> bytes``.
ENCODINGS: dict[str, dict[str, Callable[[bytes], bytes]]] = {
    "base64": {
        "encode": lambda data: _submodule("b64").encode(data).encode("ascii"),
        "decode": lambda data: _submodule("b64").decode(data),
    },
    "base64url": {
        "encode": lambda data: _submodule("b64").encode_url(data).encode("ascii"),
        "decode": lambda data: _submodule("b64").decode_url(data),
    },
    "hex": {
        "encode": lambda data: _submodule("hexutil").to_hex(data).encode("ascii"),
        "decode": lambda data: _submodule("hexutil").from_hex(data.decode("ascii")),
    },
    "qp": {
        "encode": lambda data: _submodule("quoted_printable").encode_qp(data),
        "decode": lambda data: _submodule("quoted_printable").decode_qp(data),
    },
    "uuencode": {
        "encode": lambda data: _submodule("uuencode").uuencode(data),
        "decode": lambda data: _submodule("uuencode").uudecode(data),
    },
    "ascii85": {
        "encode": lambda data: _submodule("ascii85").encode_ascii85(data),
        "decode": lambda data: _submodule("ascii85").decode_ascii85(data),
    },
    "url-quote": {
        "encode": lambda data: _submodule("url").quote(data).encode("ascii"),
        "decode": lambda data: _submodule("url").unquote(data).encode("ascii"),
    },
}


def _read(path_arg: str) -> bytes:
    """Read from ``-`` (stdin) or a real path."""

    if path_arg == "-":
        return sys.stdin.buffer.read()
    return Path(path_arg).read_bytes()


def _write(path_arg: str, payload: bytes) -> None:
    """Write to ``-`` (stdout) or a real path."""

    if path_arg == "-":
        sys.stdout.buffer.write(payload)
        sys.stdout.flush()
        return
    Path(path_arg).write_bytes(payload)


def _add_codec(parser: argparse.ArgumentParser, *, default_format: str) -> None:
    parser.add_argument(
        "-f",
        "--format",
        choices=sorted(ENCODINGS),
        default=default_format,
        help="Codec to apply.",
    )
    add_common_arguments(parser)


def _run(args: argparse.Namespace, *, op: str) -> int:
    pair = ENCODINGS[args.format]
    if op not in pair:
        raise SystemExit(f"unknown operation: {op!r}")
    try:
        payload = _read(args.input)
    except FileNotFoundError:
        print(
            style(f"input file not found: {args.input}", _cc.ANSIColors.RED),
            file=sys.stderr,
        )
        return 1
    out = pair[op](payload)
    try:
        _write(args.output, out)
    except OSError as exc:
        print(
            style(f"unable to write output: {exc}", _cc.ANSIColors.RED), file=sys.stderr
        )
        return 1
    info(f"{op} {len(payload)} bytes with {args.format}")
    success("done")
    return 0


def add_parser(parsers: object) -> None:
    """Attach ``encode`` and ``decode`` sub-commands."""

    enc = parsers.add_parser(
        "encode",
        help="Encode binary data with a named codec.",
        description="Encode data from stdin or a file using one of the codecs bundled with shredder-encryptor.",
    )
    _add_codec(enc, default_format="base64")
    enc.set_defaults(handler=lambda a: _run(a, op="encode"))

    dec = parsers.add_parser(
        "decode",
        help="Decode previously-encoded data.",
        description="Reverse a base64/hex/QP/UU/ASCII85/URL quoting produced by 'encode'.",
    )
    _add_codec(dec, default_format="base64")
    dec.set_defaults(handler=lambda a: _run(a, op="decode"))

    list_cmd = parsers.add_parser(
        "list",
        help="Show the codecs the CLI understands.",
    )
    list_cmd.set_defaults(handler=_list)


def _list(_: argparse.Namespace) -> int:
    bullet(
        [
            f"{name:10}  {pair['encode'](b'').__class__.__name__}"
            for name, pair in sorted(ENCODINGS.items())
        ]
    )
    return 0
