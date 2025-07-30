"""
EcoCycle - Configuration UI Component
Handles configuration management operations.
"""
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Table, Prompt


class ConfigurationUI(BaseUI):
    """UI component for configuration management."""

    def handle_configuration_management(self):
        """Handle configuration management interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Configuration Management[/bold cyan]")
            console.print("1. View current configuration")
            console.print("2. Set configuration value")
            console.print("3. Unset configuration value")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3"], default="0")
        else:
            print("\nConfiguration Management")
            print("1. View current configuration")
            print("2. Set configuration value")
            print("3. Unset configuration value")
            print("0. Back to main menu")

            choice = input("Select option (0-3): ").strip()

        if choice == "1":
            # View configuration
            if HAS_RICH and console:
                with console.status("[bold green]Loading configuration..."):
                    config_data = self.developer_tools.manage_configuration('view')
            else:
                print("Loading configuration...")
                config_data = self.developer_tools.manage_configuration('view')

            self._display_configuration(config_data)

        elif choice == "2":
            # Set configuration value
            key = self.get_user_input("Enter configuration key")
            value = self.get_user_input("Enter configuration value")

            if key and value:
                if HAS_RICH and console:
                    with console.status(f"[bold green]Setting {key}..."):
                        result = self.developer_tools.manage_configuration('set', key, value)
                else:
                    print(f"Setting {key}...")
                    result = self.developer_tools.manage_configuration('set', key, value)

                self.display_operation_result(result, f"Set configuration {key}")

        elif choice == "3":
            # Unset configuration value
            key = self.get_user_input("Enter configuration key to unset")

            if key and self.confirm_action(f"Unset configuration key '{key}'?"):
                if HAS_RICH and console:
                    with console.status(f"[bold yellow]Unsetting {key}..."):
                        result = self.developer_tools.manage_configuration('unset', key)
                else:
                    print(f"Unsetting {key}...")
                    result = self.developer_tools.manage_configuration('unset', key)

                self.display_operation_result(result, f"Unset configuration {key}")

    def _display_configuration(self, config_data: Dict[str, Any]):
        """Display configuration data."""
        config = config_data.get('config', {})

        if HAS_RICH and console:
            table = Table(title="Application Configuration")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Status", style="yellow")

            for key, value in config.items():
                if value == 'NOT SET':
                    status = "❌ Missing"
                elif value == '***HIDDEN***':
                    status = "🔒 Hidden"
                else:
                    status = "✅ Set"

                display_value = self.truncate_text(str(value), 50)
                table.add_row(key, display_value, status)

            console.print(table)
        else:
            print("\nApplication Configuration:")
            print("-" * 80)
            for key, value in config.items():
                if value == 'NOT SET':
                    status = "❌ Missing"
                elif value == '***HIDDEN***':
                    status = "🔒 Hidden"
                else:
                    status = "✅ Set"

                print(f"{key}: {value} ({status})")
