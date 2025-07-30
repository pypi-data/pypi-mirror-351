"""
EcoCycle - Backup & Restore UI Component
Handles backup and restore functionality.
"""
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Table, Panel, Prompt


class BackupRestoreUI(BaseUI):
    """UI component for backup and restore operations."""

    def handle_backup_restore(self):
        """Handle backup and restore interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🔄 Backup & Restore[/bold cyan]")
            console.print("1. Create backup")
            console.print("2. Restore from backup")
            console.print("3. List backups")
            console.print("4. Delete backup")
            console.print("5. Backup schedule management")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5"], default="0")
        else:
            print("\nBackup & Restore")
            print("1. Create backup")
            print("2. Restore from backup")
            print("3. List backups")
            print("4. Delete backup")
            print("5. Backup schedule management")
            print("0. Back to main menu")

            choice = input("Select option (0-5): ").strip()

        if choice == "1":
            self._create_backup()
        elif choice == "2":
            self._restore_from_backup()
        elif choice == "3":
            self._list_backups()
        elif choice == "4":
            self._delete_backup()
        elif choice == "5":
            self._backup_schedule_management()

    def _create_backup(self):
        """Create a new backup."""
        result = {'error': 'Backup cancelled or failed'}  # Initialize result

        if HAS_RICH and console:
            console.print("\n[bold cyan]Create Backup[/bold cyan]")

            # Get backup type
            backup_type = Prompt.ask(
                "Select backup type",
                choices=["full", "user", "database", "config"],
                default="full"
            )

            # Get backup name
            backup_name = self.get_user_input("Enter backup name (optional)", "")

            # Confirm backup creation
            if self.confirm_action(f"Create {backup_type} backup?"):
                with console.status(f"[bold green]Creating {backup_type} backup..."):
                    result = self.developer_tools.create_backup(backup_type, backup_name)
        else:
            print("\nCreate Backup")
            print("Available types: full, user, database, config")
            backup_type = input("Select backup type [full]: ").strip() or "full"
            backup_name = input("Enter backup name (optional): ").strip()

            if input(f"Create {backup_type} backup? (y/N): ").strip().lower() == 'y':
                print(f"Creating {backup_type} backup...")
                result = self.developer_tools.create_backup(backup_type, backup_name)

        self._display_backup_result(result)

    def _restore_from_backup(self):
        """Restore from a backup."""
        # First, list available backups
        if HAS_RICH and console:
            with console.status("[bold green]Loading available backups..."):
                backups = self.developer_tools.list_backups()
        else:
            print("Loading available backups...")
            backups = self.developer_tools.list_backups()

        if 'error' in backups:
            self.display_error(backups['error'])
            return

        backup_list = backups.get('backups', [])
        if not backup_list:
            self.display_warning("No backups available for restore")
            return

        # Display backups and get selection
        if HAS_RICH and console:
            console.print("\n[bold cyan]Available Backups:[/bold cyan]")
            table = Table(title="Backup Files")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Size", style="blue")
            table.add_column("Date", style="magenta")

            for i, backup in enumerate(backup_list, 1):
                table.add_row(
                    str(i),
                    backup.get('name', 'N/A'),
                    backup.get('type', 'N/A'),
                    self.format_bytes(backup.get('size', 0)),
                    self.format_timestamp(backup.get('created', 'N/A'))
                )

            console.print(table)

            backup_id = int(Prompt.ask("Select backup ID", choices=[str(i) for i in range(1, len(backup_list) + 1)]))
        else:
            print("\nAvailable Backups:")
            for i, backup in enumerate(backup_list, 1):
                print(f"{i}. {backup.get('name', 'N/A')} ({backup.get('type', 'N/A')}) - {backup.get('created', 'N/A')}")

            backup_id = int(input(f"Select backup ID (1-{len(backup_list)}): ").strip())

        selected_backup = backup_list[backup_id - 1]

        # Confirm restore
        if self.confirm_action(f"Restore from backup '{selected_backup.get('name', 'N/A')}'? This will overwrite current data."):
            if HAS_RICH and console:
                with console.status("[bold yellow]Restoring from backup..."):
                    result = self.developer_tools.restore_backup(selected_backup.get('filename'))
            else:
                print("Restoring from backup...")
                result = self.developer_tools.restore_backup(selected_backup.get('filename'))

            self.display_operation_result(result, "Restore from backup")

    def _list_backups(self):
        """List all available backups."""
        if HAS_RICH and console:
            with console.status("[bold green]Loading backup list..."):
                backups = self.developer_tools.list_backups()
        else:
            print("Loading backup list...")
            backups = self.developer_tools.list_backups()

        if 'error' in backups:
            self.display_error(backups['error'])
            return

        backup_list = backups.get('backups', [])

        if not backup_list:
            self.display_info("No backups found")
            return

        if HAS_RICH and console:
            table = Table(title=f"Backup Files ({len(backup_list)} total)")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Size", style="yellow")
            table.add_column("Created", style="blue")
            table.add_column("Status", style="magenta")

            for backup in backup_list:
                status = "✅ Valid" if backup.get('valid', True) else "❌ Corrupted"
                table.add_row(
                    backup.get('name', 'N/A'),
                    backup.get('type', 'N/A'),
                    self.format_bytes(backup.get('size', 0)),
                    self.format_timestamp(backup.get('created', 'N/A')),
                    status
                )

            console.print(table)
        else:
            print(f"\nBackup Files ({len(backup_list)} total):")
            print("-" * 80)
            for backup in backup_list:
                status = "✅ Valid" if backup.get('valid', True) else "❌ Corrupted"
                print(f"Name: {backup.get('name', 'N/A')}")
                print(f"  Type: {backup.get('type', 'N/A')}")
                print(f"  Size: {self.format_bytes(backup.get('size', 0))}")
                print(f"  Created: {backup.get('created', 'N/A')}")
                print(f"  Status: {status}")
                print()

    def _delete_backup(self):
        """Delete a backup file."""
        # First, list available backups
        if HAS_RICH and console:
            with console.status("[bold green]Loading backup list..."):
                backups = self.developer_tools.list_backups()
        else:
            print("Loading backup list...")
            backups = self.developer_tools.list_backups()

        if 'error' in backups:
            self.display_error(backups['error'])
            return

        backup_list = backups.get('backups', [])
        if not backup_list:
            self.display_warning("No backups available to delete")
            return

        # Display backups and get selection
        if HAS_RICH and console:
            console.print("\n[bold cyan]Select Backup to Delete:[/bold cyan]")
            for i, backup in enumerate(backup_list, 1):
                console.print(f"{i}. {backup.get('name', 'N/A')} ({backup.get('type', 'N/A')}) - {self.format_timestamp(backup.get('created', 'N/A'))}")

            backup_id = int(Prompt.ask("Select backup ID", choices=[str(i) for i in range(1, len(backup_list) + 1)]))
        else:
            print("\nSelect Backup to Delete:")
            for i, backup in enumerate(backup_list, 1):
                print(f"{i}. {backup.get('name', 'N/A')} ({backup.get('type', 'N/A')}) - {backup.get('created', 'N/A')}")

            backup_id = int(input(f"Select backup ID (1-{len(backup_list)}): ").strip())

        selected_backup = backup_list[backup_id - 1]

        # Confirm deletion
        if self.confirm_action(f"Delete backup '{selected_backup.get('name', 'N/A')}'? This cannot be undone."):
            if HAS_RICH and console:
                with console.status("[bold red]Deleting backup..."):
                    result = self.developer_tools.delete_backup(selected_backup.get('filename'))
            else:
                print("Deleting backup...")
                result = self.developer_tools.delete_backup(selected_backup.get('filename'))

            self.display_operation_result(result, "Delete backup")

    def _backup_schedule_management(self):
        """Manage backup schedules."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📅 Backup Schedule Management[/bold cyan]")
            console.print("1. View current schedule")
            console.print("2. Enable automatic backups")
            console.print("3. Disable automatic backups")
            console.print("4. Set backup frequency")
            console.print("5. Set backup time")
            console.print("6. Configure backup types")
            console.print("7. View backup history")
            console.print("8. Run backup now")
            console.print("0. Back to backup menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"], default="0")
        else:
            print("\nBackup Schedule Management")
            print("1. View current schedule")
            print("2. Enable automatic backups")
            print("3. Disable automatic backups")
            print("4. Set backup frequency")
            print("5. Set backup time")
            print("6. Configure backup types")
            print("7. View backup history")
            print("8. Run backup now")
            print("0. Back to backup menu")

            choice = input("Select option (0-8): ").strip()

        if choice == "1":
            self._view_backup_schedule()
        elif choice == "2":
            self._enable_automatic_backups()
        elif choice == "3":
            self._disable_automatic_backups()
        elif choice == "4":
            self._set_backup_frequency()
        elif choice == "5":
            self._set_backup_time()
        elif choice == "6":
            self._configure_backup_types()
        elif choice == "7":
            self._view_backup_history()
        elif choice == "8":
            self._run_backup_now()

    def _view_backup_schedule(self):
        """View current backup schedule configuration."""
        if HAS_RICH and console:
            with console.status("[bold green]Loading schedule configuration..."):
                schedule_info = self.developer_tools.get_backup_schedule()
        else:
            print("Loading schedule configuration...")
            schedule_info = self.developer_tools.get_backup_schedule()

        if 'error' in schedule_info:
            self.display_error(schedule_info['error'])
            return

        if HAS_RICH and console:
            console.print("\n[bold cyan]📅 Current Backup Schedule[/bold cyan]")

            status = "✅ Enabled" if schedule_info.get('enabled') else "❌ Disabled"
            status_color = "green" if schedule_info.get('enabled') else "red"

            schedule_panel = Panel.fit(
                f"[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]\n"
                f"[bold]Frequency:[/bold] {schedule_info.get('frequency', 'N/A').title()}\n"
                f"[bold]Backup Time:[/bold] {schedule_info.get('backup_time', 'N/A')}\n"
                f"[bold]Backup Types:[/bold] {', '.join(schedule_info.get('backup_types', []))}\n"
                f"[bold]Encryption:[/bold] {'✅ Enabled' if schedule_info.get('encryption_enabled') else '❌ Disabled'}\n"
                f"[bold]Retention Days:[/bold] {schedule_info.get('retention_days', 'N/A')}\n"
                f"[bold]Max Backups:[/bold] {schedule_info.get('max_backups', 'N/A')}\n"
                f"[bold]Last Backup:[/bold] {schedule_info.get('last_backup', 'Never')}\n"
                f"[bold]Next Backup:[/bold] {schedule_info.get('next_backup', 'Not scheduled')}",
                title="Backup Schedule Configuration",
                border_style="blue"
            )
            console.print(schedule_panel)
        else:
            print("\nCurrent Backup Schedule:")
            print("=" * 50)
            status = "✅ Enabled" if schedule_info.get('enabled') else "❌ Disabled"
            print(f"Status: {status}")
            print(f"Frequency: {schedule_info.get('frequency', 'N/A').title()}")
            print(f"Backup Time: {schedule_info.get('backup_time', 'N/A')}")
            print(f"Backup Types: {', '.join(schedule_info.get('backup_types', []))}")
            print(f"Encryption: {'✅ Enabled' if schedule_info.get('encryption_enabled') else '❌ Disabled'}")
            print(f"Retention Days: {schedule_info.get('retention_days', 'N/A')}")
            print(f"Max Backups: {schedule_info.get('max_backups', 'N/A')}")
            print(f"Last Backup: {schedule_info.get('last_backup', 'Never')}")
            print(f"Next Backup: {schedule_info.get('next_backup', 'Not scheduled')}")

    def _enable_automatic_backups(self):
        """Enable automatic backup scheduling."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📅 Enable Automatic Backups[/bold cyan]")

            frequency = Prompt.ask("Backup frequency", choices=["hourly", "daily", "weekly", "monthly"], default="daily")
            backup_time = Prompt.ask("Backup time (HH:MM)", default="02:00")
            backup_types = Prompt.ask("Backup types (comma-separated)", default="full,user,database").split(',')
            encryption = Prompt.ask("Enable encryption?", choices=["y", "n"], default="y") == "y"
            retention_days = int(Prompt.ask("Retention days", default="30"))
            max_backups = int(Prompt.ask("Maximum backups to keep", default="50"))

            with console.status("[bold green]Enabling automatic backups..."):
                result = self.developer_tools.enable_backup_schedule(
                    frequency=frequency,
                    backup_time=backup_time,
                    backup_types=[t.strip() for t in backup_types],
                    encryption_enabled=encryption,
                    retention_days=retention_days,
                    max_backups=max_backups
                )
        else:
            print("\nEnable Automatic Backups")
            print("Available frequencies: hourly, daily, weekly, monthly")
            frequency = input("Backup frequency [daily]: ").strip() or "daily"
            backup_time = input("Backup time (HH:MM) [02:00]: ").strip() or "02:00"
            backup_types_str = input("Backup types (comma-separated) [full,user,database]: ").strip() or "full,user,database"
            backup_types = [t.strip() for t in backup_types_str.split(',')]
            encryption = input("Enable encryption? (y/N): ").strip().lower() == 'y'
            retention_days = int(input("Retention days [30]: ").strip() or "30")
            max_backups = int(input("Maximum backups to keep [50]: ").strip() or "50")

            print("Enabling automatic backups...")
            result = self.developer_tools.enable_backup_schedule(
                frequency=frequency,
                backup_time=backup_time,
                backup_types=backup_types,
                encryption_enabled=encryption,
                retention_days=retention_days,
                max_backups=max_backups
            )

        self.display_operation_result(result, "Enable automatic backups")

    def _disable_automatic_backups(self):
        """Disable automatic backup scheduling."""
        if self.confirm_action("Disable automatic backups?"):
            if HAS_RICH and console:
                with console.status("[bold yellow]Disabling automatic backups..."):
                    result = self.developer_tools.disable_backup_schedule()
            else:
                print("Disabling automatic backups...")
                result = self.developer_tools.disable_backup_schedule()

            self.display_operation_result(result, "Disable automatic backups")

    def _set_backup_frequency(self):
        """Set backup frequency."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]⏰ Set Backup Frequency[/bold cyan]")
            frequency = Prompt.ask("Select frequency", choices=["hourly", "daily", "weekly", "monthly"], default="daily")

            with console.status("[bold green]Updating backup frequency..."):
                result = self.developer_tools.set_backup_frequency(frequency)
        else:
            print("\nSet Backup Frequency")
            print("Available frequencies: hourly, daily, weekly, monthly")
            frequency = input("Select frequency [daily]: ").strip() or "daily"

            print("Updating backup frequency...")
            result = self.developer_tools.set_backup_frequency(frequency)

        self.display_operation_result(result, "Set backup frequency")

    def _set_backup_time(self):
        """Set backup time."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🕐 Set Backup Time[/bold cyan]")
            backup_time = Prompt.ask("Backup time (HH:MM)", default="02:00")

            with console.status("[bold green]Updating backup time..."):
                result = self.developer_tools.set_backup_time(backup_time)
        else:
            print("\nSet Backup Time")
            backup_time = input("Backup time (HH:MM) [02:00]: ").strip() or "02:00"

            print("Updating backup time...")
            result = self.developer_tools.set_backup_time(backup_time)

        self.display_operation_result(result, "Set backup time")

    def _configure_backup_types(self):
        """Configure backup types."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]📋 Configure Backup Types[/bold cyan]")
            console.print("Available types:")
            console.print("- full: Complete system backup")
            console.print("- user: User data only")
            console.print("- database: Database only")
            console.print("- config: Configuration files only")

            backup_types = Prompt.ask("Backup types (comma-separated)", default="full,user,database").split(',')

            with console.status("[bold green]Updating backup types..."):
                result = self.developer_tools.set_backup_types([t.strip() for t in backup_types])
        else:
            print("\nConfigure Backup Types")
            print("Available types: full, user, database, config")
            backup_types_str = input("Backup types (comma-separated) [full,user,database]: ").strip() or "full,user,database"
            backup_types = [t.strip() for t in backup_types_str.split(',')]

            print("Updating backup types...")
            result = self.developer_tools.set_backup_types(backup_types)

        self.display_operation_result(result, "Configure backup types")

    def _view_backup_history(self):
        """View backup history."""
        if HAS_RICH and console:
            with console.status("[bold green]Loading backup history..."):
                history = self.developer_tools.get_backup_history()
        else:
            print("Loading backup history...")
            history = self.developer_tools.get_backup_history()

        if 'error' in history:
            self.display_error(history['error'])
            return

        history_list = history.get('history', [])

        if not history_list:
            self.display_info("No backup history found")
            return

        if HAS_RICH and console:
            table = Table(title=f"Backup History ({len(history_list)} entries)")
            table.add_column("Date", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Size", style="blue")
            table.add_column("Duration", style="magenta")

            for entry in history_list:
                status_color = "green" if entry.get('status') == 'success' else "red"
                status_text = f"[{status_color}]{entry.get('status', 'unknown').upper()}[/{status_color}]"

                table.add_row(
                    self.format_timestamp(entry.get('date', 'N/A')),
                    entry.get('type', 'N/A'),
                    status_text,
                    self.format_bytes(entry.get('size', 0)),
                    entry.get('duration', 'N/A')
                )

            console.print(table)
        else:
            print(f"\nBackup History ({len(history_list)} entries):")
            print("-" * 80)
            for entry in history_list:
                print(f"Date: {entry.get('date', 'N/A')}")
                print(f"  Type: {entry.get('type', 'N/A')}")
                print(f"  Status: {entry.get('status', 'unknown').upper()}")
                print(f"  Size: {self.format_bytes(entry.get('size', 0))}")
                print(f"  Duration: {entry.get('duration', 'N/A')}")
                print()

    def _run_backup_now(self):
        """Run a backup immediately."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]🚀 Run Backup Now[/bold cyan]")
            backup_type = Prompt.ask("Backup type", choices=["full", "user", "database", "config"], default="full")

            with console.status(f"[bold green]Running {backup_type} backup..."):
                result = self.developer_tools.run_backup_now(backup_type)
        else:
            print("\nRun Backup Now")
            print("Available types: full, user, database, config")
            backup_type = input("Backup type [full]: ").strip() or "full"

            print(f"Running {backup_type} backup...")
            result = self.developer_tools.run_backup_now(backup_type)

        self._display_backup_result(result)

    def _display_backup_result(self, result: Dict[str, Any]):
        """Display backup operation result."""
        if 'error' in result:
            self.display_error(f"Backup failed: {result['error']}")
        elif result.get('success'):
            if HAS_RICH and console:
                backup_panel = Panel.fit(
                    f"[bold]Backup Type:[/bold] {result.get('backup_type', 'N/A')}\n"
                    f"[bold]Filename:[/bold] {result.get('filename', 'N/A')}\n"
                    f"[bold]Size:[/bold] {self.format_bytes(result.get('size', 0))}\n"
                    f"[bold]Items Backed Up:[/bold] {result.get('items_backed_up', 0):,}\n"
                    f"[bold]Path:[/bold] {result.get('path', 'N/A')}",
                    title="✅ Backup Successful"
                )
                console.print(backup_panel)
            else:
                print("✅ Backup Successful")
                print(f"Backup Type: {result.get('backup_type', 'N/A')}")
                print(f"Filename: {result.get('filename', 'N/A')}")
                print(f"Size: {self.format_bytes(result.get('size', 0))}")
                print(f"Items Backed Up: {result.get('items_backed_up', 0):,}")
                print(f"Path: {result.get('path', 'N/A')}")
