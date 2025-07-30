import logging

class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[96m",    # Cyan
        "INFO": "\033[92m",     # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",    # Red
        "CRITICAL": "\033[95m", # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        msg = super().format(record)
        return f"{color}{msg}{self.RESET}"

class TkinterHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.tag_config("DEBUG", foreground="cyan")
        self.widget.tag_config("INFO", foreground="green")
        self.widget.tag_config("WARNING", foreground="orange")
        self.widget.tag_config("ERROR", foreground="red")
        self.widget.tag_config("CRITICAL", foreground="magenta")

    def emit(self, record):
        msg = self.format(record) + "\n"
        level = record.levelname
        def append():
            self.widget.insert("end", msg, level)
            self.widget.see("end")
        self.widget.after(0, append)

class LoggerManager:
    _instance = None
    _logger = None
    _gui_handler: TkinterHandler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_logger(cls, name: str = "app_logger") -> logging.Logger:
        if cls._logger is None:
            cls._logger = logging.getLogger(name)
            cls._logger.setLevel(logging.DEBUG)
            
            # Add console handler
            ch = logging.StreamHandler()
            ch.setFormatter(ColorFormatter("[%(levelname)s] %(message)s"))
            cls._logger.addHandler(ch)
        
        return cls._logger
    
    @classmethod
    def set_gui_logger(cls, widget) -> None:
        """Set up GUI logging with the provided widget."""
        # Remove existing GUI handler if any
        if cls._gui_handler:
            cls.get_logger().removeHandler(cls._gui_handler)
        
        handler = TkinterHandler(widget)
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        cls.get_logger().addHandler(handler)
        cls._gui_handler = handler
        
        return cls._logger
    
    @classmethod
    def remove_gui_logger(cls) -> None:
        """Remove the GUI logger handler."""
        if cls._gui_handler:
            cls.get_logger().removeHandler(cls._gui_handler)
            cls._gui_handler = None