import datetime
import os
import re
import threading
import time

class Colors:
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    BG_RED = "\033[41m"
    GREEN = "\033[0;32m"
    BG_GREEN = "\033[42m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    BG_BLUE = "\033[44m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    BG_YELLOW = "\033[43m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"

class Logger:
    def __init__(self, colorize=True, write_to_logfile=True, log_filename="Logger.log") -> None:
        self.COLORIZE = colorize
        self.TIME_FORMAT = "%d.%m.%Y-%H:%M:%S"
        self.log_filename = log_filename
        self.write_to_logfile = write_to_logfile
        os.system("") # Нужно для отображение цвета в консоли Windows
        if self.write_to_logfile and not os.path.isfile(self.log_filename):
            with open(self.log_filename, "w", encoding="utf-8") as file:
                file.write("")
    
    def sanitize_text(self, value: str) -> str:
        if value:
            value = re.sub(r'[\r\n\t]', ' ', value)
            value = re.sub(r'\x1b\[[0-9;]*m', '', value)
            return value.strip()
        else:
            return None

    def sanitize_color(self, value: str) -> str:
        if value:
            value = re.sub(r'[\r\n\t]', ' ', value)
            return value.strip()
        else:
            return None

    def write_to_file(self, text):
        with open(self.log_filename, "a", encoding="utf-8") as file:
            file.write(text + "\n")

    def log_info(self, message, title="Info", color=Colors.BLUE, bg_color=Colors.BLUE, TextOnly=False, WriteToFileOnly=False):
        message, title, color, bg_color = self.sanitize_text(message), self.sanitize_text(title), self.sanitize_color(color), self.sanitize_color(bg_color)
        time = datetime.datetime.now().strftime(self.TIME_FORMAT)
        if self.write_to_logfile:
            self.write_to_file(f"[{time}] - <<{title}>>: {message}")

        if WriteToFileOnly:
            return 
        
        if self.COLORIZE:
            parsed_answer = ""
            for i in range (len(message.split("$"))):
                if i % 2 == 0:
                    parsed_answer += message.split("$")[i]
                else:
                    parsed_answer += bg_color + message.split("$")[i] + Colors.END
            if TextOnly:
                print(f"{parsed_answer}")
            else:
                print(f"{color}[{time}] - <<{title}>>{Colors.END}: {parsed_answer}")
        else:
            if TextOnly:
                print(f"{message}")
            else:
                print(f"[{time}] - <<{title}>>: {message}")

    def log_success(self, message, title="Success", color=Colors.GREEN, bg_color=Colors.GREEN, TextOnly=False, WriteToFileOnly=False):
        message, title, color, bg_color = self.sanitize_text(message), self.sanitize_text(title), self.sanitize_color(color), self.sanitize_color(bg_color)
        time = datetime.datetime.now().strftime(self.TIME_FORMAT)
        if self.write_to_logfile:
            self.write_to_file(f"[{time}] - <<{title}>>: {message}")
        
        if WriteToFileOnly:
            return 
        
        if self.COLORIZE:
            parsed_answer = ""
            for i in range (len(message.split("$"))):
                if i % 2 == 0:
                    parsed_answer += message.split("$")[i]
                else:
                    parsed_answer += bg_color + message.split("$")[i] + Colors.END
            if TextOnly:
                print(f"{parsed_answer}")
            else:
                print(f"{color}[{time}] - <<{title}>>{Colors.END}: {parsed_answer}")
        else:
            if TextOnly:
                print(f"{message}")
            else:
                print(f"[{time}] - <<{title}>>: {message}")

    def log_warning(self, message, title="Warning", color=Colors.YELLOW, bg_color=Colors.YELLOW, TextOnly=False, WriteToFileOnly=False):
        message, title, color, bg_color = self.sanitize_text(message), self.sanitize_text(title), self.sanitize_color(color), self.sanitize_color(bg_color)
        time = datetime.datetime.now().strftime(self.TIME_FORMAT)
        if self.write_to_logfile:
            self.write_to_file(f"[{time}] - <<{title}>>: {message}")

        if WriteToFileOnly:
            return 
        
        if self.COLORIZE:
            parsed_answer = ""
            for i in range (len(message.split("$"))):
                if i % 2 == 0:
                    parsed_answer += message.split("$")[i]
                else:
                    parsed_answer += bg_color + message.split("$")[i] + Colors.END
            if TextOnly:
                print(f"{parsed_answer}")
            else:
                print(f"{color}[{time}] - <<{title}>>{Colors.END}: {parsed_answer}")
        else:
            if TextOnly:
                print(f"{message}")
            else:
                print(f"[{time}] - <<{title}>>: {message}")
    
    def log_error(self, message="", error=None, title="Error", color=Colors.RED, bg_color=Colors.RED, solution=None, TextOnly=False, WriteToFileOnly=False):
        time = datetime.datetime.now().strftime(self.TIME_FORMAT)
        message, title, solution, color, bg_color = self.sanitize_text(message), self.sanitize_text(title), self.sanitize_text(solution), self.sanitize_color(color), self.sanitize_color(bg_color)
        if self.write_to_logfile:
            if solution:
                self.write_to_file(f"[{time}] - <<{title}>>: {message}. Potential Solution: {solution}")
            else:
                self.write_to_file(f"[{time}] - <<{title}>>: {message}")
                
        if WriteToFileOnly:
            return 
    
        if error and title == "Error":
            title = error.__class__.__name__
            if not message:
                message = str(error)
        if self.COLORIZE:
            parsed_answer = ""
            for i in range (len(message.split("$"))):
                if i % 2 == 0:
                    parsed_answer += message.split("$")[i]
                else:
                    parsed_answer += bg_color + message.split("$")[i] + Colors.END
            if solution:
                if TextOnly:
                    print(f"{parsed_answer}. {Colors.BOLD}\nPotential Solution:{Colors.END} {Colors.CYAN}{solution}{Colors.END}")
                else:
                    print(f"{color}[{time}] - <<{title}>>{Colors.END}: {parsed_answer}. {Colors.BOLD}\nPotential Solution:{Colors.END} {Colors.CYAN}{solution}{Colors.END}")
            else:
                if TextOnly:
                    print(f"{parsed_answer}")
                else:
                    print(f"{color}[{time}] - <<{title}>>{Colors.END}: {parsed_answer}")
        else:
            if solution:
                if TextOnly:
                    print(f"[{time}] - <<{title}>>: {message}. \nPotential Solution: {solution}")
                else:
                    print(f"{message}. \nPotential Solution: {solution}")
            else:
                if TextOnly:
                    print(f"{message}")
                else:
                    print(f"[{time}] - <<{title}>>: {message}")


class StatusLogger(Logger):
    def __init__(self, status_interval_seconds=60, status_message="OK", dont_print_status=True, error_status_message="An error has occurred in the main thread"):
        super().__init__()
        self.status_interval_seconds = status_interval_seconds
        self.status_message = status_message
        self.dont_print_status = dont_print_status
        self.error_status_message = error_status_message
        self.main_thread = threading.current_thread()
        

    def __status_writer(self):
        while self.main_thread.is_alive():
            self.log_success(title="STATUS", message=self.status_message, WriteToFileOnly=self.dont_print_status)
            time.sleep(self.status_interval_seconds)
        self.log_error(title="STATUS", message=self.error_status_message)
        self.log_error(title="STATUS", message="StatusLogger has ended")

    def start(self):
        threading.Thread(target=self.__status_writer, daemon=False).start()
