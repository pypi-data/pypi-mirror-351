import importlib
from . import utils
importlib.reload(utils)
import argparse
import sys
import os
from colorama import init, Fore, Style
from .optimizer import optimize_code
from .utils import print_logo_and_welcome, print_help_message


init(autoreset=True)

def print_success(message):
    print(f"{Fore.GREEN}{Style.BRIGHT}[✓]{Style.RESET_ALL} {message}")

def print_error(message):
    print(f"{Fore.RED}{Style.BRIGHT}[!]{Style.RESET_ALL} {message}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        prog="cleanscript",
        description=f"{Fore.CYAN}CleanScript{Style.RESET_ALL}: Python Code Optimizer and Auto Commenter",
        add_help=False
    )
    
    parser.add_argument(
        "input", 
        nargs="?",
        help="Input Python file to clean and optimize"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output file (default: overwrite input)"
    )
    parser.add_argument(
        "--use-gpt", 
        action="store_true", 
        help="Use GPT for intelligent comments"
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show version information"
    )
    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help="Show this help message"
    )
    parser.add_argument(
        "--no-welcome",
        action="store_true",
        help="Skip the welcome message"
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle version flag immediately (without logo)
    if args.version:
        print("1.0.0")
        sys.exit(0)

    # Show welcome message unless --no-welcome is specified
    if not args.no_welcome:
        print_logo_and_welcome()

    # Handle help or no arguments
    if args.help or not args.input:
        print_help_message()
        sys.exit(0 if args.help else 1)

    # Rest of the processing...
    if not os.path.exists(args.input):
        print_error(f"File not found: {args.input}")
        sys.exit(1)

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            code = f.read()

        print(f"{Fore.CYAN}[i]{Style.RESET_ALL} Optimizing your code...\n")
        optimized = optimize_code(code, use_gpt=args.use_gpt)

        output_path = args.output or args.input
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(optimized)

        print_success(f"Optimization complete! Code saved to: {Fore.BLUE}{output_path}")
        if args.use_gpt:
            print(f"\n{Fore.MAGENTA}🔮 AI-powered documentation was added to your code!")
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)

    print(f"\n{Fore.YELLOW}Thanks for using {Fore.CYAN}CleanScript{Fore.YELLOW}! {Style.BRIGHT}🚀{Style.RESET_ALL}")

if __name__ == "__main__":
    main()