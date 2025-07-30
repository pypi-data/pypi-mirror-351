def add_color(color, string):
    """Adds color to text on the console (using ANSI escape codes)"""
    return f"\x1b[38;5;{color}m{string}\x1b[m"

def print_temp(string):
    """Print a temporary string to the console"""
    hide_temp()
    print(string, end="", flush=True)

def hide_temp():
    """Remove the current temporary string from the console"""
    print("\x1b[1G\x1b[2K", end="", flush=True)