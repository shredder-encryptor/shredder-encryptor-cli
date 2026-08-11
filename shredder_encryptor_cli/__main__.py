"""Main Script Run"""

from collections.abc import Callable
import sys


def main() -> None: ...  # TODO: Make this funcion in somewhere

def _get_exit_code(func: Callable) -> int:
    try:
        func()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user (Ctrl+C)", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"\nRuntime error: {exc}", file=sys.stderr)
        return 1
    else:
        return 0
    
if __name__ == "__main__":
    res = _get_exit_code(main)
    sys.exit(res)
