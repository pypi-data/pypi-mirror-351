# Logger Library #

## What is this? ##
A simple module for color logging to the console/file

## Installation ##
```bash
pip install ilyxalogger
```

## Quick Guide ##
```python
from ilyxalogger import Logger
Logger = Logger(colorize=True, write_to_logfile=True, log_filename="Logger.log")

Logger.log_info(message="Info")
Logger.log_success(message="Success")
Logger.log_warning(message="Warning")
Logger.log_error(message="Error", error=ValueError, solution="Potential solution")
```
Also if you add a symbol `$`, the framed text will be highlighted in color.

Example of output modification:
```python
color = "\033[0;35m" # ANSII PURPLE
bg_color = "\033[41m" # ANSII RED, color for text in $..$
message="Some $warning$ message"
title="MyWarning"

log_warning(message=message, title=title, color=color, bg_color=bg_color)
```

Output example:

![image](https://github.com/user-attachments/assets/23ec14e0-d554-404d-87f9-511e45ef801b)