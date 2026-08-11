# shredder-encryptor-cli

A colourful command-line front-end for
[`shredder-encryptor`](https://github.com/shredder-encryptor/shredder-encryptor).
Everything is built on top of the standard-library `argparse`; the only
external dependency is the `shredder-encryptor` package itself.

## Install

```bash
pip install shredder-encryptor-cli
```

## Usage

The CLI exposes three top-level groups:

```text
shredder-cli
├── encode / decode / list     # base64, hex, qp, uuencode, ascii85, url-quote
├── encrypt / decrypt / ciphers
│     # vigenere, xor-stream, feistel-ecb, feistel-cbc, sha256
└── key save / load / list / remove
```

### Encode

```bash
$ echo -n "hello" | shredder-cli encode --format base64
aGVsbG8NCg==i encode 7 bytes with base64
✓ done
```

### Encrypt

```bash
$ shredder-cli encrypt --cipher feistel-cbc \
    --key "my-key" --encoding hex \
    --input msg.txt --output msg.enc
```

## Colours

The CLI follows the [`NO_COLOR`](https://no-color.org/) convention:

| environment     | effect                    |
| --------------- | ------------------------- |
| unset, TTY      | colours on, Windows VT    |
| `NO_COLOR=1`    | plain text                |
| `SHREEDER_COLOR=never` | plain text         |
| `SHREEDER_COLOR=always` | colours even when piped |

## I can't use!

See more? [Install it!](#install)

## License

MIT.  See [LICENSE](LICENSE).