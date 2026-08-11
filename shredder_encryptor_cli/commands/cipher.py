"""``cipher`` sub-commands: encrypt / decrypt with the bundled ciphers."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

from .._argparse import add_common_arguments, style
from .. import color_code as _cc
from ..ui import info, success, warn

__all__ = ["add_parser", "CIPHERS"]


def _build_vigenere(key: bytes):
    from shredder_encryptor.cipher import VigenereCipher

    return VigenereCipher(key=key)


def _build_xor(key: bytes):
    from shredder_encryptor.cipher import XorStreamCipher

    return XorStreamCipher(key=key)


def _build_ecb(key: bytes):
    from shredder_encryptor.cipher import FeistelEcbCipher

    return FeistelEcbCipher(key=key)


def _build_cbc(key: bytes):
    from shredder_encryptor.cipher import FeistelCbcCipher

    return FeistelCbcCipher(key=key)


def _build_sha(key: bytes):
    from shredder_encryptor.cipher import Sha256Hash

    return Sha256Hash(salt=key)


#: Maps cipher name to ``(builder, reversible)``.  ``builder(key)``
#: returns a :class:`framework.BaseCipher` instance.
CIPHERS: dict[str, tuple[Callable[[bytes], object], bool]] = {
    "vigenere": (_build_vigenere, True),
    "xor-stream": (_build_xor, True),
    "feistel-ecb": (_build_ecb, True),
    "feistel-cbc": (_build_cbc, True),
    "sha256": (_build_sha, False),
}


def _read(path_arg: str) -> bytes:
    if path_arg == "-":
        return sys.stdin.buffer.read()
    return Path(path_arg).read_bytes()


def _write(path_arg: str, payload: bytes) -> None:
    if path_arg == "-":
        sys.stdout.buffer.write(payload)
        sys.stdout.flush()
        return
    Path(path_arg).write_bytes(payload)


def _hex_decode(text: str) -> bytes:
    from shredder_encryptor.codec.hexutil import from_hex

    return from_hex(text.strip())


def _hex_encode(data: bytes) -> str:
    from shredder_encryptor.codec.hexutil import to_hex

    return to_hex(data)


def _run(args: argparse.Namespace, *, op: str) -> int:
    builder, reversible = CIPHERS[args.cipher]
    if op == "decrypt" and not reversible:
        warn(f"{args.cipher} is a one-way cipher and cannot be decrypted")
        return 1
    try:
        key = (
            _hex_decode(args.key)
            if args.key_format == "hex"
            else args.key.encode("utf-8")
        )
    except (ValueError, UnicodeEncodeError) as exc:
        print(style(f"invalid key: {exc}", _cc.ANSIColors.RED), file=sys.stderr)
        return 1
    if not key:
        print(style("key must not be empty", _cc.ANSIColors.RED), file=sys.stderr)
        return 1
    cipher_obj = builder(key)
    try:
        payload = _read(args.input)
    except FileNotFoundError:
        print(
            style(f"input file not found: {args.input}", _cc.ANSIColors.RED),
            file=sys.stderr,
        )
        return 1
    method = getattr(cipher_obj, op)
    out = method(payload)
    if args.encoding == "hex" and op != "decrypt":
        out_text = _hex_encode(out) + "\n"
        _write(args.output, out_text.encode("ascii"))
    elif args.encoding == "hex" and op == "decrypt":
        # Accept either raw hex or hex with whitespace.
        out = _hex_decode(out.decode("ascii"))
        _write(args.output, out)
    else:
        _write(args.output, out)
    info(f"{op} {len(payload)} bytes with {args.cipher}")
    success("done")
    return 0


def add_parser(parsers: object) -> None:
    enc = parsers.add_parser(
        "encrypt",
        help="Encrypt data with a bundled cipher.",
        description="Encrypt stdin or a file using one of the example ciphers in shredder_encryptor.cipher.",
    )
    _add_cipher_args(enc)
    enc.set_defaults(handler=lambda a: _run(a, op="encrypt"))

    dec = parsers.add_parser(
        "decrypt",
        help="Decrypt data produced by 'encrypt'.",
    )
    _add_cipher_args(dec)
    dec.set_defaults(handler=lambda a: _run(a, op="decrypt"))

    list_cmd = parsers.add_parser(
        "ciphers",
        help="List the ciphers the CLI understands.",
    )
    list_cmd.set_defaults(handler=_list)


def _add_cipher_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-c",
        "--cipher",
        choices=sorted(CIPHERS),
        default="feistel-cbc",
        help="Cipher to apply.",
    )
    parser.add_argument(
        "-k",
        "--key",
        required=True,
        help="Encryption key (text by default; --key-format hex accepts hex).",
    )
    parser.add_argument(
        "--key-format",
        choices=("text", "hex"),
        default="text",
        help="How to interpret --key.",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        choices=("raw", "hex"),
        default="hex",
        help="Output encoding. 'hex' prints hex; 'raw' prints raw bytes.",
    )
    add_common_arguments(parser)


def _list(_: argparse.Namespace) -> int:
    for name, (_, reversible) in sorted(CIPHERS.items()):
        marker = "reversible" if reversible else "one-way"
        print(
            style(f"  {name:<13} ", _cc.ANSIColors.GREEN)
            + style(marker, _cc.ANSIColors.GREY)
        )
    return 0
