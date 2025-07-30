from colorama import init, Fore, Style
from pyfiglet import Figlet
from termcolor import colored
init(autoreset=True)

def print_logo_and_welcome():
    f = Figlet(font='slant', width=180)
    print(colored(f.renderText('CLEAN'), 'light_cyan') + 
    colored(f.renderText('SCRIPT'), 'light_magenta'))
    logo = rf"""
{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}┌───────────────────────────────────────────────────────┐
│      The Ultimate Python Code Optimizer & Docum       │
└───────────────────────────────────────────────────────┘
"""
    print(logo)

def print_help_message():
    print(f"{Fore.YELLOW}🌟 {Fore.WHITE}Key Features:")
    print(f"{Fore.CYAN}  • Automatic code optimization")
    print(f"{Fore.CYAN}  • Intelligent comment generation")
    print(f"{Fore.CYAN}  • Readme file creation")
    print(f"{Fore.CYAN}  • PEP-8 compliance checks")
    
    print(f"\n{Fore.YELLOW}🚀 {Fore.WHITE}Basic Commands:")
    print(f"{Fore.GREEN}  cleanscript [file.py]             {Fore.LIGHTBLACK_EX}- Optimize & clean your code")
    print(f"{Fore.GREEN}  cleanscript [file.py] --use-gpt   {Fore.LIGHTBLACK_EX}- Add AI-powered comments")
    print(f"{Fore.GREEN}  cleanscript [file.py] -o [output] {Fore.LIGHTBLACK_EX}- Save to specific file")
    print(f"{Fore.GREEN}  cleanscript --version             {Fore.LIGHTBLACK_EX}- Show version info")
    print(f"{Fore.GREEN}  cleanscript --help                {Fore.LIGHTBLACK_EX}- Show full help")
    
    print(f"\n{Fore.MAGENTA}💡 Tip: Run with {Fore.WHITE}--use-gpt{Fore.MAGENTA} for AI-assisted documentation!")
    print(f"{Fore.LIGHTBLUE_EX}\n🔗 GitHub: https://github.com/yourusername/cleanscript")
    print(f"{Style.BRIGHT}{Fore.WHITE}\nLet's make your Python code shine! ✨{Style.RESET_ALL}\n")