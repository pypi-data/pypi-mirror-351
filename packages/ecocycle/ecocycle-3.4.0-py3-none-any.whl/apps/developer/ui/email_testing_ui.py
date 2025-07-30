"""
EcoCycle - Email Testing UI Component
Handles email system testing functionality.
"""
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Panel, Table, Prompt


class EmailTestingUI(BaseUI):
    """UI component for email system testing."""

    def handle_email_system_testing(self):
        """Handle email system testing interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Email System Testing[/bold cyan]")
            console.print("1. Check email configuration")
            console.print("2. Send test email")
            console.print("3. Validate email templates")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3"], default="0")
        else:
            print("\nEmail System Testing")
            print("1. Check email configuration")
            print("2. Send test email")
            print("3. Validate email templates")
            print("0. Back to main menu")

            choice = input("Select option (0-3): ").strip()

        if choice == "1":
            # Check email configuration
            if HAS_RICH and console:
                with console.status("[bold green]Checking email configuration..."):
                    email_data = self.developer_tools.test_email_system()
            else:
                print("Checking email configuration...")
                email_data = self.developer_tools.test_email_system()

            self._display_email_config(email_data)

        elif choice == "2":
            # Send test email
            test_email = self.get_user_input("Enter test email address")

            if test_email:
                if HAS_RICH and console:
                    with console.status(f"[bold green]Sending test email to {test_email}..."):
                        result = self.developer_tools.test_email_system(test_email)
                else:
                    print(f"Sending test email to {test_email}...")
                    result = self.developer_tools.test_email_system(test_email)

                self._display_email_test_result(result)

        elif choice == "3":
            # Validate email templates
            if HAS_RICH and console:
                with console.status("[bold green]Validating email templates..."):
                    template_data = self.developer_tools.test_email_system()
            else:
                print("Validating email templates...")
                template_data = self.developer_tools.test_email_system()

            self._display_email_templates(template_data)

    def _display_email_config(self, email_data: Dict[str, Any]):
        """Display email configuration status."""
        smtp_config = email_data.get('smtp_config', {})
        template_check = email_data.get('template_check', {})

        if HAS_RICH and console:
            console.print("\n[bold cyan]Email Configuration Status[/bold cyan]")

            # SMTP Configuration
            smtp_panel = Panel.fit(
                "\n".join([f"[bold]{key}:[/bold] {'✅ SET' if value == 'SET' else '❌ NOT SET'}"
                          for key, value in smtp_config.items()]),
                title="SMTP Configuration"
            )
            console.print(smtp_panel)

            # Template Status
            if 'error' not in template_check:
                template_status = "\n".join([f"[bold]{template}:[/bold] ✅ {info['size']} bytes"
                                           for template, info in template_check.items()
                                           if isinstance(info, dict)])
                template_panel = Panel.fit(template_status or "No templates found", title="Email Templates")
                console.print(template_panel)
            else:
                console.print(f"[red]Template Error: {template_check['error']}[/red]")

        else:
            print("\nEmail Configuration Status:")
            print("=" * 50)
            print("SMTP Configuration:")
            for key, value in smtp_config.items():
                status = "✅ SET" if value == 'SET' else "❌ NOT SET"
                print(f"  {key}: {status}")

            print("\nEmail Templates:")
            if 'error' not in template_check:
                for template, info in template_check.items():
                    if isinstance(info, dict):
                        print(f"  {template}: ✅ {info['size']} bytes")
            else:
                print(f"  Error: {template_check['error']}")

    def _display_email_test_result(self, result: Dict[str, Any]):
        """Display email test results."""
        test_results = result.get('test_results', {})

        if HAS_RICH and console:
            console.print("\n[bold cyan]Email Test Results[/bold cyan]")

            if 'error' in test_results:
                console.print(f"[red]❌ Test failed: {test_results['error']}[/red]")
            else:
                success = test_results.get('email_sent', False)
                status = "✅ SUCCESS" if success else "❌ FAILED"

                result_panel = Panel.fit(
                    f"[bold]Status:[/bold] {status}\n"
                    f"[bold]Recipient:[/bold] {test_results.get('recipient', 'N/A')}\n"
                    f"[bold]Test Code:[/bold] {test_results.get('test_code', 'N/A')}",
                    title="Test Results"
                )
                console.print(result_panel)

        else:
            print("\nEmail Test Results:")
            print("=" * 50)
            if 'error' in test_results:
                print(f"❌ Test failed: {test_results['error']}")
            else:
                success = test_results.get('email_sent', False)
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"Status: {status}")
                print(f"Recipient: {test_results.get('recipient', 'N/A')}")
                print(f"Test Code: {test_results.get('test_code', 'N/A')}")

    def _display_email_templates(self, template_data: Dict[str, Any]):
        """Display email template validation results."""
        template_check = template_data.get('template_check', {})

        if HAS_RICH and console:
            console.print("\n[bold cyan]Email Template Validation[/bold cyan]")

            if 'error' in template_check:
                console.print(f"[red]Error: {template_check['error']}[/red]")
            else:
                table = Table(title="Email Templates")
                table.add_column("Template", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Size", style="yellow")

                for template, info in template_check.items():
                    if isinstance(info, dict):
                        table.add_row(
                            template,
                            "✅ Valid",
                            self.format_bytes(info['size'])
                        )

                console.print(table)

        else:
            print("\nEmail Template Validation:")
            print("=" * 50)
            if 'error' in template_check:
                print(f"Error: {template_check['error']}")
            else:
                for template, info in template_check.items():
                    if isinstance(info, dict):
                        print(f"{template}: ✅ Valid ({self.format_bytes(info['size'])})")
