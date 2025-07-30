#!/usr/bin/env python3
"""
EcoCycle - Dependency Manager Module
Provides automatic installation of missing packages when needed.
"""
import importlib.util
import logging
import subprocess
import sys
import time
import os
import json
import socket
from typing import List, Dict, Tuple, Union, Optional, Set, Any, cast

# Import config module for paths
try:
    import config.config as config
    # Use config module for log directory
    LOG_DIR = config.LOG_DIR
    CACHE_DIR = config.CACHE_DIR
except ImportError:
    # Fallback if config module is not available
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Logs')
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'cache')

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(LOG_DIR, 'dependency_manager.log'))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Path for dependency cache file
DEPENDENCY_CACHE_FILE = os.path.join(CACHE_DIR, 'dependency_cache.json')

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # We'll install tqdm first when needed

# Dictionary mapping feature names to required packages
FEATURE_DEPENDENCIES = {
    'visualization': ['matplotlib', 'numpy', 'plotly'],
    'route_planning': ['folium', 'requests'],
    'data_export': ['fpdf', 'tabulate'],
    'social_sharing': ['pillow', 'qrcode'],
    'enhanced_ui': ['colorama', 'blessed', 'termcolor'],
    'notifications': ['sendgrid', 'twilio'],
    'sheets_integration': ['google-api-python-client', 'google-auth', 'google-auth-oauthlib'],
    'ai_features': ['openai', 'google-generativeai'],
    'core': ['colorama', 'python-dotenv', 'tqdm']
}

# Cache of checked packages to avoid repeated checks
_package_cache: Dict[str, bool] = {}

def _load_package_cache() -> None:
    """Load package installation cache from file."""
    global _package_cache
    try:
        if os.path.exists(DEPENDENCY_CACHE_FILE):
            with open(DEPENDENCY_CACHE_FILE, 'r') as f:
                _package_cache = json.load(f)
                logger.debug(f"Loaded package cache with {len(_package_cache)} entries")
    except Exception as e:
        logger.error(f"Error loading package cache: {e}")
        _package_cache = {}

def _save_package_cache() -> None:
    """Save package installation cache to file."""
    try:
        with open(DEPENDENCY_CACHE_FILE, 'w') as f:
            json.dump(_package_cache, f)
            logger.debug(f"Saved package cache with {len(_package_cache)} entries")
    except Exception as e:
        logger.error(f"Error saving package cache: {e}")

# Load cache at module initialization
_load_package_cache()


def reset_package_cache(package_name: Optional[str] = None) -> None:
    """
    Reset the package installation check cache.

    Args:
        package_name: If provided, only reset cache for this package.
                     If None, reset the entire cache.
    """
    global _package_cache
    if package_name is None:
        _package_cache = {}
        logger.debug("Package installation cache completely reset")
    elif package_name in _package_cache:
        del _package_cache[package_name]
        logger.debug(f"Package installation cache reset for {package_name}")

    # Save the updated cache to file
    _save_package_cache()

def is_package_installed(package_name: str, force_check: bool = False) -> bool:
    """
    Check if a Python package is installed.
    Uses a cache to avoid repeated checks for the same package.

    Args:
        package_name: Name of the package to check
        force_check: If True, bypass the cache and force a fresh check

    Returns:
        True if the package is installed, False otherwise
    """
    # Check cache first unless force_check is True
    if not force_check and package_name in _package_cache:
        return _package_cache[package_name]

    # Handle package name conversion for import
    import_name = package_name.replace('-', '_')

    # Special cases
    if package_name == 'google-api-python-client':
        import_name = 'googleapiclient'
    elif package_name == 'python-dotenv':
        import_name = 'dotenv'
    elif package_name == 'google-auth-oauthlib':
        import_name = 'google_auth_oauthlib'
    elif package_name == 'google-generativeai':
        import_name = 'google.generativeai'

    # Check if package can be imported
    is_installed = importlib.util.find_spec(import_name) is not None

    # If not found by find_spec, try direct import as fallback
    # This helps with packages that have complex module structures
    if not is_installed:
        try:
            __import__(import_name)
            is_installed = True
        except ImportError:
            is_installed = False

    # Update cache
    _package_cache[package_name] = is_installed
    logger.debug(f"Package '{package_name}' installed status: {is_installed}")

    # Save the updated cache to file
    _save_package_cache()

    return is_installed


def verify_package_installation(package_name: str) -> bool:
    """
    Verify that a package is actually installed and importable.
    This is more thorough than just checking pip's return code.

    Args:
        package_name: Name of the package to verify

    Returns:
        True if the package can be imported, False otherwise
    """
    # Reset the cache for this package to force a fresh check
    if package_name in _package_cache:
        del _package_cache[package_name]

    # Use is_package_installed with force_check=True to verify
    return is_package_installed(package_name, force_check=True)


def ensure_package(package_name: str, silent: bool = False, max_retries: int = 2) -> bool:
    """
    Ensure a single package is installed, installing it if needed.
    Includes retry mechanism and verification.

    Args:
        package_name: Name of the package to ensure
        silent: If True, suppress progress display
        max_retries: Maximum number of installation attempts (default: 2)

    Returns:
        True if package is available (already installed or successfully installed),
        False if installation failed after retries
    """
    # Move global statement to the top of the function scope
    global TQDM_AVAILABLE

    # Force a fresh check bypassing the cache to see current state
    already_installed = is_package_installed(package_name, force_check=True)

    if already_installed:
        # Only log to debug logs, don't print to console
        logger.info(f"Package '{package_name}' is already installed.")
        return True

    if not silent:
        print(f"Attempting to install required package: {package_name}")
    logger.info(f"Attempting to install required package: {package_name}")

    # Track retry attempts
    retry_count = 0

    while retry_count <= max_retries:
        if retry_count > 0:
            logger.info(f"Retry attempt {retry_count} for package: {package_name}")
            if not silent:
                print(f"Retry attempt {retry_count} for package: {package_name}")

        try:
            # Ensure tqdm is available for progress display if not silent
            if not TQDM_AVAILABLE and package_name != 'tqdm' and not silent:
                print("Installing 'tqdm' for progress display...")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tqdm'],
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
                    from tqdm import tqdm
                    TQDM_AVAILABLE = True
                    print("'tqdm' installed successfully.")
                except Exception as tqdm_e:
                    logger.warning(f"Could not install tqdm automatically: {tqdm_e}")
                    TQDM_AVAILABLE = False # Ensure it's marked as unavailable

            # Prepare installation command
            install_command = [sys.executable, '-m', 'pip', 'install', package_name]

            # Execute installation
            if TQDM_AVAILABLE and not silent:
                try:
                    # Import tqdm again to ensure it's available in this scope
                    from tqdm import tqdm
                    # Custom tqdm animation with cycling characters
                    # This creates a more engaging loading animation during installation
                    spinner_chars = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'  # String instead of list for ascii parameter
                    with tqdm(total=100, desc=f"Installing {package_name}",
                             bar_format="{desc}: {percentage:3.0f}% |{bar}| [{elapsed}<{remaining}]",
                             ascii=True, colour='green') as pbar:
                        process = subprocess.Popen(
                            install_command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )

                        # Simulate progress while waiting for the process to complete
                        i = 0
                        while process.poll() is None:
                            pbar.update(1)  # Increment by 1%
                            pbar.set_description(f"Installing {package_name} {spinner_chars[i % len(spinner_chars)]}")
                            i += 1
                            time.sleep(0.1)  # Small delay for animation
                            if pbar.n >= 90:  # Cap at 90% until we know it's done
                                pbar.n = 80
                                pbar.refresh()

                        # Process completed, get output
                        _, stderr = process.communicate()  # Ignore stdout, only need stderr for error reporting

                        # Complete the progress bar
                        pbar.n = 100
                        pbar.refresh()

                        if process.returncode != 0:
                            logger.error(f"Error installing {package_name} with tqdm: {stderr}")
                            if not silent:
                                print(f"\nError installing {package_name}. Details logged. Try: pip install {package_name}")
                            # Don't return False here, let the retry mechanism handle it
                            raise RuntimeError(f"Installation failed with return code {process.returncode}")
                except Exception as install_e:
                    # Catch potential exceptions during Popen/communicate
                    logger.error(f"Exception during installation of {package_name} with tqdm: {install_e}")
                    if not silent:
                        print(f"\nAn exception occurred during installation of {package_name}.")
                    # Don't return False here, let the retry mechanism handle it
                    raise install_e

            else: # No tqdm or silent install
                try:
                    subprocess.check_call(
                        install_command,
                        stdout=subprocess.DEVNULL, # Suppress output
                        stderr=subprocess.DEVNULL  # Suppress errors from console (they are logged)
                    )
                except subprocess.CalledProcessError as e:
                    # Log the specific error from CalledProcessError if available
                    stderr_output = "No stderr output captured"
                    if hasattr(e, 'stderr') and e.stderr:
                        try:
                            stderr_output = e.stderr.decode()
                        except (AttributeError, UnicodeDecodeError):
                            stderr_output = str(e.stderr)
                    logger.error(f"Error installing {package_name} (silent/no tqdm): Command '{e.cmd}' returned non-zero exit status {e.returncode}. Stderr: {stderr_output}")
                    if not silent:
                        print(f"\nError installing {package_name}. Please install it manually with: pip install {package_name}")
                    # Don't return False here, let the retry mechanism handle it
                    raise e
                except Exception as e:
                     logger.error(f"General error installing {package_name} (silent/no tqdm): {e}")
                     if not silent:
                         print(f"\nError installing {package_name}. Please install it manually with: pip install {package_name}")
                     # Don't return False here, let the retry mechanism handle it
                     raise e

            # Verify the installation was successful by trying to import the package
            if verify_package_installation(package_name):
                # Update the cache on successful installation and verification
                _package_cache[package_name] = True
                _save_package_cache()
                logger.info(f"Successfully installed and verified package: {package_name}")
                if not silent:
                     print(f"Successfully installed {package_name}.")
                return True
            else:
                # Package didn't install correctly despite pip reporting success
                logger.warning(f"Package {package_name} was installed but cannot be imported. Retrying...")
                if not silent:
                    print(f"Package {package_name} was installed but cannot be imported. Retrying...")
                # Continue to next retry attempt
                retry_count += 1
                continue

        except Exception as e:
            # Catch any broader errors in the logic
            logger.error(f"Failed to ensure package {package_name} (attempt {retry_count+1}/{max_retries+1}): {str(e)}")
            if not silent:
                print(f"\nError during installation process for {package_name}: {str(e)}")

            # Increment retry counter
            retry_count += 1

            # If we've reached max retries, return False
            if retry_count > max_retries:
                logger.error(f"Max retries ({max_retries}) reached for package {package_name}. Installation failed.")
                if not silent:
                    print(f"Max retries reached for package {package_name}. Installation failed.")
                return False

            # Wait a moment before retrying
            time.sleep(1)
            continue

    # If we get here, all retries failed
    return False


def ensure_feature(feature_name: str, silent: bool = False, max_retries: int = 2) -> Tuple[bool, List[str]]:
    """
    Ensure all packages required for a specific feature are installed.

    Args:
        feature_name: Name of the feature requiring packages
        silent: If True, suppress progress display
        max_retries: Maximum number of installation attempts per package

    Returns:
        Tuple of (success, failed_packages):
            - success: True if all packages are available
            - failed_packages: List of packages that failed to install
    """
    if feature_name not in FEATURE_DEPENDENCIES:
        logger.warning(f"Unknown feature: {feature_name}")
        return True, []

    packages = FEATURE_DEPENDENCIES[feature_name]
    failed_packages = []

    if not silent and not TQDM_AVAILABLE:
        # Try to install tqdm first for better user experience
        ensure_package('tqdm', silent=True, max_retries=max_retries)

    # Log the start of feature installation
    logger.info(f"Installing packages for feature: {feature_name}")
    if not silent:
        print(f"\nInstalling packages for feature: {feature_name}")
        print(f"Required packages: {', '.join(packages)}")

    for package in packages:
        if not ensure_package(package, silent, max_retries):
            failed_packages.append(package)
            logger.warning(f"Failed to install package {package} for feature {feature_name}")
        else:
            logger.info(f"Successfully installed package {package} for feature {feature_name}")

    success = len(failed_packages) == 0

    # Log the result of feature installation
    if success:
        logger.info(f"Successfully installed all packages for feature: {feature_name}")
        if not silent:
            print(f"Successfully installed all packages for feature: {feature_name}")
    else:
        logger.error(f"Failed to install some packages for feature {feature_name}: {', '.join(failed_packages)}")
        if not silent:
            print(f"Failed to install some packages for feature {feature_name}: {', '.join(failed_packages)}")

    return success, failed_packages


def ensure_packages(package_list: List[str], silent: bool = False, max_retries: int = 2) -> Tuple[bool, List[str]]:
    """
    Ensure multiple packages are installed.

    Args:
        package_list: List of packages to ensure
        silent: If True, suppress progress display
        max_retries: Maximum number of installation attempts per package

    Returns:
        Tuple of (success, failed_packages):
            - success: True if all packages are available
            - failed_packages: List of packages that failed to install
    """
    failed_packages = []

    if not silent and not TQDM_AVAILABLE:
        # Try to install tqdm first for better user experience
        ensure_package('tqdm', silent=True, max_retries=max_retries)

    # Log the start of package installation
    logger.info(f"Installing packages: {', '.join(package_list)}")
    if not silent:
        print(f"\nInstalling packages: {', '.join(package_list)}")

    for package in package_list:
        if not ensure_package(package, silent, max_retries):
            failed_packages.append(package)
            logger.warning(f"Failed to install package: {package}")
        else:
            logger.info(f"Successfully installed package: {package}")

    success = len(failed_packages) == 0

    # Log the result of package installation
    if success:
        logger.info("Successfully installed all packages")
        if not silent:
            print("Successfully installed all packages")
    else:
        logger.error(f"Failed to install some packages: {', '.join(failed_packages)}")
        if not silent:
            print(f"Failed to install some packages: {', '.join(failed_packages)}")

    return success, failed_packages


def check_all_dependencies() -> Dict[str, Dict[str, Union[bool, List[str]]]]:
    """
    Check all defined dependencies across all features.

    Returns:
        Dictionary with results for each feature
    """
    results = {}

    for feature, packages in FEATURE_DEPENDENCIES.items():
        missing = []
        for package in packages:
            if not is_package_installed(package):
                missing.append(package)

        results[feature] = {
            'available': len(missing) == 0,
            'missing': missing
        }

    return results


def get_feature_for_package(package_name: str) -> List[str]:
    """
    Find which features require a specific package.

    Args:
        package_name: Name of the package to find features for

    Returns:
        List of feature names that require this package
    """
    features = []
    for feature, packages in FEATURE_DEPENDENCIES.items():
        if package_name in packages:
            features.append(feature)
    return features


def check_system_dependencies() -> Dict[str, bool]:
    """
    Check for system-level dependencies that might be required.

    Returns:
        Dictionary mapping dependency names to availability status
    """
    system_deps = {
        'pip': False,
        'python': False,
        'git': False,
        'internet_connection': False
    }

    # Check pip
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', '--version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        system_deps['pip'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        system_deps['pip'] = False

    # Check Python version
    system_deps['python'] = sys.version_info >= (3, 6)

    # Check git
    try:
        subprocess.check_call(
            ['git', '--version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        system_deps['git'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        system_deps['git'] = False

    # Check internet connection by trying to connect to a reliable host
    try:
        subprocess.check_call(
            ['ping', '-c', '1', 'pypi.org'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        system_deps['internet_connection'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try an alternative method if ping is not available
        try:
            # socket is already imported at the top of the file
            socket.create_connection(("pypi.org", 443), timeout=5)
            system_deps['internet_connection'] = True
        except (socket.timeout, socket.error, OSError):
            system_deps['internet_connection'] = False

    return system_deps


def run_diagnostics(fix_issues: bool = False) -> Dict[str, Any]:
    """
    Run comprehensive diagnostics on the dependency system.

    Args:
        fix_issues: If True, attempt to fix issues automatically

    Returns:
        Dictionary with diagnostic results
    """
    results = {
        'system_dependencies': check_system_dependencies(),
        'package_dependencies': check_all_dependencies(),
        'issues_found': 0,
        'issues_fixed': 0,
        'issues_details': []
    }

    # Count issues in system dependencies
    for dep, available in results['system_dependencies'].items():
        if not available:
            results['issues_found'] += 1
            results['issues_details'].append(f"System dependency '{dep}' is not available")

    # Count issues in package dependencies
    for feature, status in results['package_dependencies'].items():
        if not status['available']:
            missing_count = len(status['missing'])
            results['issues_found'] += missing_count
            for package in status['missing']:
                results['issues_details'].append(f"Package '{package}' required by feature '{feature}' is not installed")

    # Try to fix issues if requested
    if fix_issues and results['issues_found'] > 0:
        logger.info("Attempting to fix dependency issues automatically")

        # Fix package dependencies
        for feature, status in results['package_dependencies'].items():
            if not status['available']:
                logger.info(f"Attempting to install missing packages for feature '{feature}'")
                success, failed = ensure_feature(feature, silent=False, max_retries=2)

                if success:
                    results['issues_fixed'] += len(status['missing'])
                    logger.info(f"Successfully fixed all package dependencies for feature '{feature}'")
                else:
                    results['issues_fixed'] += len(status['missing']) - len(failed)
                    logger.warning(f"Could not fix all package dependencies for feature '{feature}'. Still missing: {', '.join(failed)}")

    return results


if __name__ == "__main__":
    # When run directly, check and report on all dependencies
    print("EcoCycle Dependency Manager")
    print("==========================")

    # Check for command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--doctor' or sys.argv[1] == '--diagnostics':
            # Run diagnostics mode
            fix_issues = '--fix' in sys.argv
            print(f"Running dependency diagnostics{' with auto-fix' if fix_issues else ''}...")

            results = run_diagnostics(fix_issues)

            print("\nSystem Dependencies:")
            for dep, available in results['system_dependencies'].items():
                print(f"  {dep}: {'Available' if available else 'Not Available'}")

            print("\nFeature Dependencies:")
            for feature, status in results['package_dependencies'].items():
                print(f"\n{feature}:")
                print(f"  Available: {'Yes' if status['available'] else 'No'}")
                if status['missing']:
                    missing_packages = cast(List[str], status['missing'])
                    print(f"  Missing packages: {', '.join(missing_packages)}")

            print(f"\nIssues found: {results['issues_found']}")
            if fix_issues:
                print(f"Issues fixed: {results['issues_fixed']}")
                if results['issues_fixed'] < results['issues_found']:
                    print(f"Issues remaining: {results['issues_found'] - results['issues_fixed']}")

            if results['issues_details']:
                print("\nIssue Details:")
                for issue in results['issues_details']:
                    print(f"  - {issue}")

            sys.exit(0)

    # Default behavior: check and offer to install missing packages
    results = check_all_dependencies()

    print("\nFeature Dependency Status:")
    for feature, status in results.items():
        print(f"\n{feature}:")
        print(f"  Available: {'Yes' if status['available'] else 'No'}")
        if status['missing']:
            # Cast to ensure type safety
            missing_packages = cast(List[str], status['missing'])
            print(f"  Missing packages: {', '.join(missing_packages)}")

            # Offer to install
            install = input(f"\nInstall missing packages for {feature}? (y/n): ")
            if install.lower() == 'y':
                success, failed = ensure_feature(feature)
                if success:
                    print(f"All packages for {feature} installed successfully!")
                else:
                    print(f"Some packages for {feature} could not be installed: {', '.join(failed)}")

    print("\nTip: Run with --doctor to perform comprehensive diagnostics")
    print("     Add --fix to automatically fix issues")
