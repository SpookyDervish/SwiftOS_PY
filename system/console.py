import os
import shutil

from textual.widgets import RichLog

from rich.text import Text
from rich.align import Align

from enum import Enum


ASCII_LOGO = rf"""
  /$$$$$$ 
 /$$__  $$
| $$  \__/
|  $$$$$$ 
 \____  $$
 /$$  \ $$
|  $$$$$$/
 \______/ 
"""
ASCII_LOGO_COLOURS = [
    "#881177",
    "#aa3355",
    "#cc6666",
    "#ee9944",
    "#eedd00",
    "#99dd55",
    "#44dd88",
    "#22ccbb",
    "#00bbcc",
    "#0099cc",
    "#3366bb",
    "#663399",
]


def ascii_logo_text() -> Text:
    """Get the ascii logo"""
    return Text(ASCII_LOGO)

def ascii_logo_rainbow() -> Text:
    """Get the ascii logo, with a rainbow effect"""
    lines = ASCII_LOGO.splitlines(keepends=True)
    return Text.assemble(*zip(lines, ASCII_LOGO_COLOURS))

def console_bounds():
    return shutil.get_terminal_size()

def center_text(text : Text, width : int = console_bounds().columns):
    return Align(
        text,
        align="center",
        width=width
    )
    
def rule_line(rich_log : RichLog, style: str = ""):
    width = rich_log.min_width
    
    rule_line = f"[{style}]" + ("-" * width) + f"[/{style}]"
    rich_log.write(rule_line)
    
class LogLevel(Enum):
    OK = 1
    INFO = 2
    DEBUG = 3
    WARNING = 4
    ERROR = 5
    FATAL = 6
    
def log(rich_log : RichLog, message: str, log_level : LogLevel = LogLevel.OK):
    style = ""
    prefix = ""

    if log_level == LogLevel.OK:
        style = "green"
        prefix = "OK"
    elif log_level == LogLevel.INFO:
        style = "cyan"
        prefix = "INFO"
    elif log_level == LogLevel.DEBUG:
        style = "bright_cyan"
        prefix = "DEBUG"
    elif log_level == LogLevel.WARNING:
        style = "white on gold1"
        prefix = "WARN"
    elif log_level == LogLevel.ERROR:
        style = "red"
        prefix = "ERROR"
    elif log_level == LogLevel.FATAL:
        style = "white on red"
        prefix = "FATAL"
    else:
        style = "white on magenta"
        prefix = "???"
        
    rich_log.write(f"[bold][[{style}]{prefix}[/{style}]][/bold] {message}")