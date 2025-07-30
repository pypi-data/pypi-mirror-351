#!/usr/bin/env python3
"""
EcoCycle - Dependency Installer Script
This script installs all required dependencies for the EcoCycle application.
"""
import subprocess
import sys
import os

def print_header():
    """Print a nice header for the installer."""
    print("\n" + "=" * 60)
    print("EcoCycle Dependency Installer".center(60))
    print("=" * 60)
    print("\nThis script will install all required dependencies for EcoCycle.")
    print("It will use pip to install packages directly, bypassing the dependency manager.")

def install_package(package_name):
    """Install a single package using pip."""
    print(f"\nInstalling {package_name}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        print(f"✓ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package_name}: {e}")
        return False

def main():
    """Main installer function."""
    print_header()
    
    # Core dependencies
    core_deps = ['colorama', 'python-dotenv', 'tqdm']
    
    # Feature-specific dependencies
    feature_deps = {
        'visualization': ['matplotlib', 'numpy', 'plotly'],
        'route_planning': ['folium', 'requests'],
        'data_export': ['fpdf', 'tabulate'],
        'social_sharing': ['pillow', 'qrcode'],
        'enhanced_ui': ['blessed', 'termcolor'],
        'notifications': ['sendgrid', 'twilio'],
        'sheets_integration': ['google-api-python-client', 'google-auth', 'google-auth-oauthlib'],
        'ai_features': ['openai', 'google-generativeai']
    }
    
    # Install core dependencies first
    print("\nInstalling core dependencies...")
    for package in core_deps:
        install_package(package)
    
    # Ask which features to install
    print("\nWhich features would you like to install dependencies for?")
    for i, feature in enumerate(feature_deps.keys(), 1):
        print(f"{i}. {feature}")
    print("0. All features")
    
    choice = input("\nEnter your choice (0-8, or 'q' to quit): ")
    
    if choice.lower() == 'q':
        print("\nExiting installer.")
        return
    
    try:
        choice = int(choice)
        if choice == 0:
            # Install all dependencies
            print("\nInstalling dependencies for all features...")
            for feature, packages in feature_deps.items():
                print(f"\n--- {feature.upper()} ---")
                for package in packages:
                    install_package(package)
        elif 1 <= choice <= len(feature_deps):
            # Install dependencies for selected feature
            feature = list(feature_deps.keys())[choice - 1]
            print(f"\nInstalling dependencies for {feature}...")
            for package in feature_deps[feature]:
                install_package(package)
        else:
            print("\nInvalid choice. Exiting.")
            return
    except ValueError:
        print("\nInvalid input. Exiting.")
        return
    
    print("\nDependency installation complete!")
    print("You can now run the EcoCycle application.")

if __name__ == "__main__":
    main()
