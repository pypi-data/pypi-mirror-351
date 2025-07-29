from datetime import datetime
from colorama import init
import sys

init()

class Logger:
    def __init__(self, prefix: str = None, indent: int = 0):
        self.colors = {
            'white': "\u001b[37m",
            'magenta': "\x1b[38;2;157;38;255m",
            'red': "\x1b[38;5;196m",
            'green': "\x1b[38;5;40m",
            'yellow': "\x1b[38;5;220m",
            'blue': "\x1b[38;5;21m",
            'lightblue': "\x1b[94m",
            'pink': "\x1b[38;5;176m",
            'gray': "\x1b[90m",
            'cyan': "\x1b[96m"
        }
        self.prefix: str = f"{self.colors['gray']}[{self.colors['magenta']}{prefix}{self.colors['gray']}] {self.colors['white']}| " if prefix else ""
        self.indent: str = " " * indent
        self.debug_mode: bool = any(arg.lower() in ['--debug', '-debug'] for arg in sys.argv)

    def get_time(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def get_taken(self, start: float = None, end: float = None) -> str:
        if start is not None and end is not None:
            if start > 1e12: start, end = start/1000, end/1000
            duration = abs(end - start)
            return f"{duration * 1e6:.2f}".rstrip('0').rstrip('.') + "µs" if duration < 0.001 else \
                f"{duration * 1e3:.2f}".rstrip('0').rstrip('.') + "ms" if duration < 1 else \
                f"{duration:.2f}".rstrip('0').rstrip('.') + "s"
        return ""

    def _log(self, color: str, message: str, level: str, start: int = None, end: int = None) -> None:
        time_now = f"{self.colors['gray']}[{self.colors['magenta']}{self.get_time()}{self.colors['gray']}] {self.colors['white']}|"
        taken = self.get_taken(start, end)
        timer = f" {self.colors['magenta']}In{self.colors['white']} -> {self.colors['magenta']}{taken}" if taken else ""
        print(f"{self.indent}{self.prefix}{time_now} {self.colors['gray']}[{color}{level}{self.colors['gray']}] {self.colors['white']}-> {self.colors['gray']}[{color}{message}{self.colors['gray']}]{timer}")

    def success(self, message: str, level: str = "SCC", start: int = None, end: int = None) -> None:
        self._log(self.colors['green'], message, level, start, end)

    def warning(self, message: str, level: str = "WRN", start: int = None, end: int = None) -> None:
        self._log(self.colors['yellow'], message, level, start, end)

    def info(self, message: str, level: str = "INF", start: int = None, end: int = None) -> None:
        self._log(self.colors['lightblue'], message, level, start, end)

    def failure(self, message: str, level: str = "ERR", start: int = None, end: int = None) -> None:
        self._log(self.colors['red'], message, level, start, end)

    def debug(self, message: str, level: str = "DBG", start: int = None, end: int = None) -> None:
        if self.debug_mode: self._log(self.colors['magenta'], message, level, start, end)

    def captcha(self, message: str, level: str = "CAP", start: int = None, end: int = None) -> None:
        self._log(self.colors['cyan'], message, level, start, end)

    def PETC(self):
        input(f"{self.indent}{self.colors['gray']}[{self.colors['magenta']}Press Enter To Continue{self.colors['gray']}]")

    def __getattr__(self, name):
        if name.upper() in self.colors:
            def color(message: str, level: str = name.capitalize(), start: int = None, end: int = None):
                self._log(self.colors[name.upper()], message, level, start, end)
            return color
        raise AttributeError(f"'{self.__class__.__name__}' object has no attr '{name}'")