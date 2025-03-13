class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GREY = '\033[90m'

def format_message(level, message, color):
    return f"{Colors.BOLD}{color}[{level}] {Colors.RESET}{message}"
def info(message):
    print(format_message("INFO", message, Colors.BLUE))
def success(message):
    print(format_message("SUCCESS", message, Colors.GREEN))
def warning(message):
    print(format_message("WARNING", message, Colors.YELLOW))
def error(message):
    print(format_message("ERROR", message, Colors.RED))
def debug(message):
    print(format_message("DEBUG", message, Colors.CYAN))
def critical(message):
    print(format_message("CRITICAL", message, Colors.MAGENTA))
def custom_msg(message, color=Colors.WHITE, prefix="LOG"):
    print(format_message(prefix, message, color))
def divider(char="=", length=50, color=Colors.WHITE):
    """Prints a colored divider line."""
    print(f"{color}{char * length}{Colors.RESET}")
def section_header(title, char="=", length=50, color=Colors.WHITE):
    """Prints a centered section header with a divider."""
    padding = (length - len(title) - 2) // 2  # For centering the title
    line = f"{char * padding} {title.upper()} {char * padding}"
    if len(line) < length:
        line += char  # Adjust for odd lengths
    print(f"{color}{line}{Colors.RESET}")

"""
    # Example usage 
    info("This is an informational message.")
    success("Operation completed successfully!")
    warning("This is a warning. Proceed with caution.")
    error("An error occurred while processing the data.")
    debug("Debugging variable x: 42")
    critical("Critical failure! System shutting down.")
    custom_msg("This is a custom log with a star!", color=Colors.YELLOW, prefix="★ CUSTOM ★")

    divider()
    section_header("Starting Process")
    divider("~", 50, color=Colors.BLUE)
    section_header("Process Complete", char="*", color=Colors.GREEN)
"""