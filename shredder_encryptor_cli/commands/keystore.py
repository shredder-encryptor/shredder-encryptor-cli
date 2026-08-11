"""``key`` sub-commands: thin wrapper around :mod:`shredder_encryptor.persistence`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .._argparse import style
from .. import color_code as _cc
from ..ui import error, info, success, warn

__all__ = ["add_parser"]


def _read_payload(value: str) -> bytes:
    """Read a key payload from ``-`` (stdin) or a file path."""

    if value == "-":
        return sys.stdin.buffer.read()
    return Path(value).read_bytes()


def add_parser(parsers: object) -> None:
    parent = parsers.add_parser(
        "key",
        help="Store, load and list keys in the on-disk key store.",
        description="Manage keys with the persistent key store from shredder-encryptor.",
    )
    sub = parent.add_subparsers(dest="key_command", required=True)

    save = sub.add_parser("save", help="Persist a key under a name.")
    save.add_argument("name", help="Name to store the key under.")
    save.add_argument(
        "-d",
        "--data",
        default="-",
        help="Key bytes to store ('-' for stdin or a file path).",
    )
    save.add_argument(
        "--dir",
        metavar="DIR",
        default=None,
        help="Override the default key directory.",
    )
    save.add_argument(
        "--overwrite", action="store_true", help="Overwrite an existing key."
    )
    save.set_defaults(handler=_save)

    load = sub.add_parser("load", help="Print the bytes of a stored key.")
    load.add_argument("name", help="Name of the key to load.")
    load.add_argument(
        "--dir",
        metavar="DIR",
        default=None,
        help="Override the default key directory.",
    )
    load.set_defaults(handler=_load)

    ls = sub.add_parser("list", help="List stored keys.")
    ls.add_argument(
        "--dir",
        metavar="DIR",
        default=None,
        help="Override the default key directory.",
    )
    ls.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove leftover .tmp files first.",
    )
    ls.set_defaults(handler=_list)

    rm = sub.add_parser("remove", help="Delete a stored key.")
    rm.add_argument("name", help="Name of the key to delete.")
    rm.add_argument(
        "--dir",
        metavar="DIR",
        default=None,
        help="Override the default key directory.",
    )
    rm.add_argument(
        "--force", action="store_true", help="Do not raise on a missing key."
    )
    rm.set_defaults(handler=_remove)


def _save(args: argparse.Namespace) -> int:
    from shredder_encryptor.persistence import KeyStoreError, save_key

    try:
        payload = _read_payload(args.data)
    except FileNotFoundError:
        error(f"data file not found: {args.data}")
        return 1
    try:
        path = save_key(
            args.name,
            payload,
            args.dir,
            overwrite=args.overwrite,
        )
    except KeyStoreError as exc:
        error(str(exc))
        return 1
    success(f"saved '{args.name}' to {path}")
    return 0


def _load(args: argparse.Namespace) -> int:
    from shredder_encryptor.persistence import KeyStoreError, load_key

    try:
        data = load_key(args.name, args.dir)
    except KeyStoreError as exc:
        error(str(exc))
        return 1
    sys.stdout.buffer.write(data)
    sys.stdout.flush()
    info(f"loaded {len(data)} bytes")
    return 0


def _list(args: argparse.Namespace) -> int:
    from shredder_encryptor.persistence import KeyStoreError, list_keys

    try:
        names = list_keys(args.dir, cleanup=args.cleanup)
    except KeyStoreError as exc:
        error(str(exc))
        return 1
    if not names:
        warn("no keys stored")
        return 0
    for name in names:
        marker = style("  - ", _cc.ANSIColors.GREEN)
        print(f"{marker}{name}")
    return 0


def _remove(args: argparse.Namespace) -> int:
    from shredder_encryptor.persistence import KeyStoreError, delete_key

    try:
        removed = delete_key(args.name, args.dir, missing_ok=args.force)
    except KeyStoreError as exc:
        error(str(exc))
        return 1
    if removed:
        success(f"removed '{args.name}'")
    else:
        info(f"'{args.name}' was not present (--force)")
    return 0
