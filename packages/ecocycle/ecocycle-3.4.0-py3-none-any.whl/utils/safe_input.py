"""
EcoCycle - Safe Input Utilities
Provides safe input functions that handle KeyboardInterrupt gracefully.
"""
import sys
import getpass
from typing import Optional, List


def safe_input(prompt: str = "", default: str = "", allow_empty: bool = True) -> Optional[str]:
    """
    Safe input function that handles KeyboardInterrupt gracefully.

    Args:
        prompt: The input prompt to display
        default: Default value if user presses Enter
        allow_empty: Whether to allow empty input

    Returns:
        User input string or None if cancelled
    """
    try:
        user_input = input(prompt).strip()
        if not user_input and default:
            return default
        if not user_input and not allow_empty:
            return safe_input(prompt, default, allow_empty)
        return user_input
    except KeyboardInterrupt:
        print("\n")  # New line for better formatting
        print("Input cancelled by user.")

        # Ask user if they want to exit or continue
        try:
            choice = input("\nDo you want to exit EcoCycle? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                print("\nThank you for using EcoCycle! Goodbye.")
                print("With ♡ - the EcoCycle team.")
                sys.exit(0)
            else:
                print("Returning to previous menu...")
                return None
        except KeyboardInterrupt:
            # If user presses Ctrl+C again, force exit
            print("\n\nThank you for using EcoCycle! Goodbye.")
            print("With ♡ - the EcoCycle team.")
            sys.exit(0)


def safe_password_input(prompt: str = "Password: ") -> Optional[str]:
    """
    Safe password input function that handles KeyboardInterrupt gracefully.

    Args:
        prompt: The password prompt to display

    Returns:
        Password string or None if cancelled
    """
    try:
        return getpass.getpass(prompt)
    except KeyboardInterrupt:
        print("\n")  # New line for better formatting
        print("Password input cancelled by user.")

        # Ask user if they want to exit or continue
        try:
            choice = input("\nDo you want to exit EcoCycle? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                print("\nThank you for using EcoCycle! Goodbye.")
                print("With ♡ - the EcoCycle team.")
                sys.exit(0)
            else:
                print("Returning to previous menu...")
                return None
        except KeyboardInterrupt:
            # If user presses Ctrl+C again, force exit
            print("\n\nThank you for using EcoCycle! Goodbye.")
            print("With ♡ - the EcoCycle team.")
            sys.exit(0)


def safe_menu_choice(prompt: str, choices: List[str], default: str = "1") -> Optional[str]:
    """
    Safe menu choice function that handles KeyboardInterrupt gracefully.

    Args:
        prompt: The menu prompt to display
        choices: List of valid choices
        default: Default choice if user presses Enter

    Returns:
        User choice or None if cancelled
    """
    try:
        choice = input(f"{prompt} ({'/'.join(choices)}): ").strip()
        if not choice:
            choice = default
        if choice in choices:
            return choice
        else:
            print(f"Invalid choice. Please select from: {', '.join(choices)}")
            return safe_menu_choice(prompt, choices, default)
    except KeyboardInterrupt:
        print("\n")  # New line for better formatting
        print("Menu selection cancelled by user.")

        # Ask user if they want to exit or continue
        try:
            exit_choice = input("\nDo you want to exit EcoCycle? (y/n): ").lower().strip()
            if exit_choice in ['y', 'yes']:
                print("\nThank you for using EcoCycle! Goodbye.")
                print("With ♡ - the EcoCycle team.")
                sys.exit(0)
            else:
                print("Returning to previous menu...")
                return None
        except KeyboardInterrupt:
            # If user presses Ctrl+C again, force exit
            print("\n\nThank you for using EcoCycle! Goodbye.")
            print("With ♡ - the EcoCycle team.")
            sys.exit(0)


def safe_numeric_input(prompt: str, min_value: Optional[float] = None,
                      max_value: Optional[float] = None,
                      input_type: type = float) -> Optional[float]:
    """
    Safe numeric input function that handles KeyboardInterrupt gracefully.

    Args:
        prompt: The input prompt to display
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        input_type: Type of numeric input (int or float)

    Returns:
        Numeric value or None if cancelled
    """
    try:
        user_input = input(prompt).strip()
        if not user_input:
            return None

        try:
            value = input_type(user_input)

            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}")
                return safe_numeric_input(prompt, min_value, max_value, input_type)

            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}")
                return safe_numeric_input(prompt, min_value, max_value, input_type)

            return value
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")
            return safe_numeric_input(prompt, min_value, max_value, input_type)

    except KeyboardInterrupt:
        print("\n")  # New line for better formatting
        print("Numeric input cancelled by user.")

        # Ask user if they want to exit or continue
        try:
            choice = input("\nDo you want to exit EcoCycle? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                print("\nThank you for using EcoCycle! Goodbye.")
                print("With ♡ - the EcoCycle team.")
                sys.exit(0)
            else:
                print("Returning to previous menu...")
                return None
        except KeyboardInterrupt:
            # If user presses Ctrl+C again, force exit
            print("\n\nThank you for using EcoCycle! Goodbye.")
            print("With ♡ - the EcoCycle team.")
            sys.exit(0)


def safe_confirmation(prompt: str, default: bool = False) -> Optional[bool]:
    """
    Safe confirmation function that handles KeyboardInterrupt gracefully.

    Args:
        prompt: The confirmation prompt to display
        default: Default value if user presses Enter

    Returns:
        Boolean confirmation or None if cancelled
    """
    default_text = "Y/n" if default else "y/N"
    try:
        choice = input(f"{prompt} ({default_text}): ").lower().strip()
        if not choice:
            return default
        if choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")
            return safe_confirmation(prompt, default)
    except KeyboardInterrupt:
        print("\n")  # New line for better formatting
        print("Confirmation cancelled by user.")

        # Ask user if they want to exit or continue
        try:
            exit_choice = input("\nDo you want to exit EcoCycle? (y/n): ").lower().strip()
            if exit_choice in ['y', 'yes']:
                print("\nThank you for using EcoCycle! Goodbye.")
                print("With ♡ - the EcoCycle team.")
                sys.exit(0)
            else:
                print("Returning to previous menu...")
                return None
        except KeyboardInterrupt:
            # If user presses Ctrl+C again, force exit
            print("\n\nThank you for using EcoCycle! Goodbye.")
            print("With ♡ - the EcoCycle team.")
            sys.exit(0)


def handle_keyboard_interrupt(func):
    """
    Decorator to handle KeyboardInterrupt gracefully in functions.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n")  # New line for better formatting
            print("Operation cancelled by user.")

            # Ask user if they want to exit or continue
            try:
                choice = input("\nDo you want to exit EcoCycle? (y/n): ").lower().strip()
                if choice in ['y', 'yes']:
                    print("\nThank you for using EcoCycle! Goodbye.")
                    print("With ♡ - the EcoCycle team.")
                    sys.exit(0)
                else:
                    print("Returning to main menu...")
                    return None
            except KeyboardInterrupt:
                # If user presses Ctrl+C again, force exit
                print("\n\nThank you for using EcoCycle! Goodbye.")
                print("With ♡ - the EcoCycle team.")
                sys.exit(0)
    return wrapper
