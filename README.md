# shredder-encryptor-cli

A colourful command-line front-end for
[`shredder-encryptor`](https://github.com/shredder-encryptor/shredder-encryptor).
Everything is built on top of the standard-library `argparse`; the only
external dependency is the `shredder-encryptor` package itself.

## Install

The project is not published on PyPI yet; install it from the sibling
checkout:

```bash
git clone https://github.com/shredder-encryptor/shredder-encryptor-cli
cd shredder-encryptor-cli
python -m pip install -e .
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
i info encode 5 bytes with base64
+ success done
aGVsbG8=
```

### Encrypt

```bash
$ shredder-cli encrypt --cipher feistel-cbc \
    --key "my-key" --encoding hex \
    --input msg.txt --output msg.enc
```

### Key store

```bash
$ shredder-cli key save demo --data - < token.bin
$ shredder-cli key list
  - demo
$ shredder-cli key load demo > token.bin
```

## Colours

The CLI follows the [`NO_COLOR`](https://no-color.org/) convention:

| environment     | effect                    |
| --------------- | ------------------------- |
| unset, TTY      | colours on, Windows VT    |
| `NO_COLOR=1`    | plain text                |
| `SHREEDER_COLOR=never` | plain text         |
| `SHREEDER_COLOR=always` | colours even when piped |

## License

MIT.  See [LICENSE](LICENSE).