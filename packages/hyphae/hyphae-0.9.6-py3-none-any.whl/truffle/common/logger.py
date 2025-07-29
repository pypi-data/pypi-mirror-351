import os
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Colors:
    MAIN: str = "\033[38;2;95;173;235m"      # #5FADEB - Primary actions/success
    SECONDARY: str = "\033[38;2;74;155;217m"  # #4A9BD9 - Info/progress
    DIM_GRAY: str = "\033[38;2;128;128;128m"  # #808080 - Technical details
    ERROR: str = "\033[38;2;255;59;48m"       # #FF3B30 - Errors
    WARNING: str = "\033[38;2;255;149;0m"     # #FF9500 - Warnings
    RESET: str = "\033[0m"

@dataclass
class Symbols:
    SUCCESS: str = "✓"
    ERROR: str = "✗"
    WARNING: str = "!"
    INFO: str = "ℹ"
    PROMPT: str = "❯"

class Logger:
    def __init__(self) -> None:
        pass

    def success(self, message: str, end: str = "\n") -> None:
        print(f"{Colors.MAIN}{Symbols.SUCCESS} {message}{Colors.RESET}", end=end)

    def error(self, message: str, end: str = "\n") -> None:
        print(f"{Colors.ERROR}{Symbols.ERROR} {message}{Colors.RESET}", end=end)

    def warning(self, message: str, end: str = "\n") -> None:
        print(f"{Colors.WARNING}{Symbols.WARNING} {message}{Colors.RESET}", end=end)
    
    def info(self, message: str, end: str = "\n") -> None:
        print(f"{Colors.SECONDARY}{Symbols.INFO} {message}{Colors.RESET}", end=end)
    
    def plain_info(self, message: str, end: str = "\n") -> None:
        print(f"{Colors.SECONDARY}{message}{Colors.RESET}", end=end)

    def input(self, message: str) -> str:
        return input(f"{Colors.SECONDARY}{Symbols.PROMPT} {message}{Colors.RESET}")

    def debug(self, message: str, end: str = "\n") -> None:
        if os.getenv("TRUFFLE_DEBUG"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Colors.DIM_GRAY}[{timestamp}] {Symbols.INFO} {message}{Colors.RESET}", end=end)