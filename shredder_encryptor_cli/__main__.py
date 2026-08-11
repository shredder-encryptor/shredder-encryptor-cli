"""Allow ``python -m shredder_encryptor_cli``."""

from __future__ import annotations

import sys
from collections.abc import Callable

__all__ = ["main", "_get_exit_code"]


def main() -> int:
    from .main import main as _main

    return _main()


def _get_exit_code(func: Callable[..., int]) -> int:
    try:
        return int(func())
    except KeyboardInterrupt:
        from .ui import warn

        warn("interrupted by user (Ctrl+C)")
        return 130
    except Exception as exc:  # pragma: no cover - defensive
        from .ui import error

        error(f"unexpected error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(_get_exit_code(main))
