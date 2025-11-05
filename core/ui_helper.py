"""
UI Helper - Centralized UI/UX for Proto Gear CLI
Consolidates print statements into reusable, testable methods
"""

# ANSI Color codes
class Colors:
    """ANSI escape codes for terminal colors"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'


class UIHelper:
    """Centralized UI helper for consistent terminal output"""

    @staticmethod
    def success(message: str):
        """Print success message with green color"""
        print(f"{Colors.GREEN}{message}{Colors.ENDC}")

    @staticmethod
    def error(message: str):
        """Print error message with red color"""
        print(f"{Colors.FAIL}{message}{Colors.ENDC}")

    @staticmethod
    def warning(message: str):
        """Print warning message with yellow color"""
        print(f"{Colors.WARNING}{message}{Colors.ENDC}")

    @staticmethod
    def info(message: str):
        """Print info message with cyan color"""
        print(f"{Colors.CYAN}{message}{Colors.ENDC}")

    @staticmethod
    def gray(message: str):
        """Print gray/dim message"""
        print(f"{Colors.GRAY}{message}{Colors.ENDC}")

    @staticmethod
    def header(message: str, color=Colors.YELLOW):
        """Print bold header"""
        print(f"{color}{Colors.BOLD}{message}{Colors.ENDC}")

    @staticmethod
    def separator(char='=', length=60):
        """Print separator line"""
        print(char * length)

    @staticmethod
    def blank_line():
        """Print blank line"""
        print()

    @staticmethod
    def section(title: str):
        """Print section header with separator"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.ENDC}")
        print("-" * 30)

    @staticmethod
    def welcome(main_text: str, subtitle: str = ""):
        """Print welcome message"""
        print(f"{Colors.GREEN}{main_text}{Colors.ENDC}")
        if subtitle:
            print(f"{Colors.GRAY}{subtitle}{Colors.ENDC}\n")

    @staticmethod
    def farewell(message: str = "Happy coding! May your builds be swift and your bugs be few."):
        """Print farewell message"""
        print(f"{Colors.GRAY}{message}{Colors.ENDC}\n")

    @staticmethod
    def list_item(text: str, prefix: str = "  ", symbol: str = "+"):
        """Print list item"""
        print(f"{prefix}{symbol} {text}")

    @staticmethod
    def command(cmd: str, description: str = ""):
        """Print command with optional description"""
        if description:
            print(f"  {Colors.BOLD}{cmd}{Colors.ENDC} - {description}")
        else:
            print(f"  {Colors.BOLD}{cmd}{Colors.ENDC}")

    @staticmethod
    def step(number: int, description: str):
        """Print numbered step"""
        print(f"  {number}. {description}")

    @staticmethod
    def file_created(filename: str):
        """Print file creation message"""
        print(f"  {Colors.GREEN}✓{Colors.ENDC} {filename}")

    @staticmethod
    def file_skipped(filename: str, reason: str = "not selected"):
        """Print file skipped message"""
        print(f"  {Colors.GRAY}⊘ {filename} ({reason}){Colors.ENDC}")

    @staticmethod
    def prompt(message: str):
        """Print prompt message"""
        print(f"{Colors.CYAN}{message}{Colors.ENDC}")

    @staticmethod
    def example(text: str):
        """Print example text in gray"""
        print(f"{Colors.GRAY}{text}{Colors.ENDC}")

    @staticmethod
    def next_steps_header():
        """Print next steps header"""
        print(f"\n{Colors.YELLOW}Next steps:{Colors.ENDC}")

    @staticmethod
    def centered(text: str, width: int = 80):
        """Print centered text"""
        print(text.center(width))

    @staticmethod
    def box_header(title: str, width: int = 60):
        """Print boxed header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.ENDC}")
        UIHelper.separator('=', width)

    @staticmethod
    def validation_error(message: str):
        """Print validation error"""
        print(f"{Colors.YELLOW}{message}{Colors.ENDC}")

    @staticmethod
    def section_with_content(title: str, items: list):
        """Print section with list of items"""
        UIHelper.header(title)
        for item in items:
            if isinstance(item, str):
                print(f"  {item}")
            else:
                print(f"  {item}")
        print()

    @staticmethod
    def config_summary(title: str, config: dict):
        """Print configuration summary"""
        UIHelper.info(f"\n{title}")
        for key, value in config.items():
            print(f"  {key}: {Colors.BOLD}{value}{Colors.ENDC}")


# Convenience instance for importing
ui = UIHelper()
