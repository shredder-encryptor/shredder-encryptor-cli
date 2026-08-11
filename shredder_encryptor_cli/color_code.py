"""ANSI Color Codes."""


# from _colorize.py
class ANSIColors:
    RESET: str = "\x1b[0m"

    BLACK: str = "\x1b[30m"
    BLUE: str = "\x1b[34m"
    CYAN: str = "\x1b[36m"
    GREEN: str = "\x1b[32m"
    GREY: str = "\x1b[90m"
    MAGENTA: str = "\x1b[35m"
    RED: str = "\x1b[31m"
    WHITE: str = "\x1b[37m"
    YELLOW: str = "\x1b[33m"

    BOLD: str = "\x1b[1m"
    BOLD_BLACK: str = "\x1b[1;30m"
    BOLD_BLUE: str = "\x1b[1;34m"
    BOLD_CYAN: str = "\x1b[1;36m"
    BOLD_GREEN: str = "\x1b[1;32m"
    BOLD_MAGENTA: str = "\x1b[1;35m"
    BOLD_RED: str = "\x1b[1;31m"
    BOLD_WHITE: str = "\x1b[1;37m"
    BOLD_YELLOW: str = "\x1b[1;33m"

    # intense = like bold but without being bold
    INTENSE_BLACK: str = "\x1b[90m"
    INTENSE_BLUE: str = "\x1b[94m"
    INTENSE_CYAN: str = "\x1b[96m"
    INTENSE_GREEN: str = "\x1b[92m"
    INTENSE_MAGENTA: str = "\x1b[95m"
    INTENSE_RED: str = "\x1b[91m"
    INTENSE_WHITE: str = "\x1b[97m"
    INTENSE_YELLOW: str = "\x1b[93m"

    BACKGROUND_BLACK: str = "\x1b[40m"
    BACKGROUND_BLUE: str = "\x1b[44m"
    BACKGROUND_CYAN: str = "\x1b[46m"
    BACKGROUND_GREEN: str = "\x1b[42m"
    BACKGROUND_MAGENTA: str = "\x1b[45m"
    BACKGROUND_RED: str = "\x1b[41m"
    BACKGROUND_WHITE: str = "\x1b[47m"
    BACKGROUND_YELLOW: str = "\x1b[43m"

    INTENSE_BACKGROUND_BLACK: str = "\x1b[100m"
    INTENSE_BACKGROUND_BLUE: str = "\x1b[104m"
    INTENSE_BACKGROUND_CYAN: str = "\x1b[106m"
    INTENSE_BACKGROUND_GREEN: str = "\x1b[102m"
    INTENSE_BACKGROUND_MAGENTA: str = "\x1b[105m"
    INTENSE_BACKGROUND_RED: str = "\x1b[101m"
    INTENSE_BACKGROUND_WHITE: str = "\x1b[107m"
    INTENSE_BACKGROUND_YELLOW: str = "\x1b[103m"
