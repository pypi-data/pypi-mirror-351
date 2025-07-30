"""
EcoCycle - Data Management UI Component
Handles database management and user data operations.
"""
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Table, Panel, Prompt


class DataManagementUI(BaseUI):
    """UI component for data management operations."""

    def handle_database_management(self):
        """Handle database management interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Database Management[/bold cyan]")
            console.print("1. View all tables")
            console.print("2. View specific table")
            console.print("3. Table statistics")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3"], default="0")
        else:
            print("\nDatabase Management")
            print("1. View all tables")
            print("2. View specific table")
            print("3. Table statistics")
            print("0. Back to main menu")

            choice = input("Select option (0-3): ").strip()

        if choice == "1":
            # View all tables
            if HAS_RICH and console:
                with console.status("[bold green]Loading database contents..."):
                    db_data = self.developer_tools.view_database_contents()
            else:
                print("Loading database contents...")
                db_data = self.developer_tools.view_database_contents()

            self._display_database_overview(db_data)

        elif choice == "2":
            # View specific table
            if HAS_RICH and console:
                table_name = Prompt.ask("Enter table name")
                limit = int(Prompt.ask("Number of rows to display", default="10"))
            else:
                table_name = input("Enter table name: ").strip()
                limit = int(input("Number of rows to display [10]: ").strip() or "10")

            if HAS_RICH and console:
                with console.status(f"[bold green]Loading {table_name} data..."):
                    table_data = self.developer_tools.view_database_contents(table_name, limit)
            else:
                print(f"Loading {table_name} data...")
                table_data = self.developer_tools.view_database_contents(table_name, limit)

            self._display_table_data(table_name, table_data)

        elif choice == "3":
            # Table statistics
            if HAS_RICH and console:
                with console.status("[bold green]Calculating table statistics..."):
                    db_data = self.developer_tools.view_database_contents()
            else:
                print("Calculating table statistics...")
                db_data = self.developer_tools.view_database_contents()

            self._display_table_statistics(db_data)

    def _display_database_overview(self, db_data: Dict[str, Any]):
        """Display database overview."""
        if 'error' in db_data:
            self.display_error(db_data['error'])
            return

        if HAS_RICH and console:
            table = Table(title="Database Tables Overview")
            table.add_column("Table Name", style="cyan")
            table.add_column("Columns", style="green")
            table.add_column("Total Rows", style="yellow")
            table.add_column("Sample Data", style="dim")

            for table_name, table_info in db_data.items():
                columns = ", ".join(table_info.get('columns', []))
                total_rows = str(table_info.get('total_count', 0))
                sample_rows = len(table_info.get('sample_rows', []))

                table.add_row(
                    table_name,
                    columns[:50] + "..." if len(columns) > 50 else columns,
                    total_rows,
                    f"{sample_rows} rows shown"
                )

            console.print(table)
        else:
            print("\nDatabase Tables Overview:")
            print("-" * 80)
            for table_name, table_info in db_data.items():
                print(f"Table: {table_name}")
                print(f"  Columns: {', '.join(table_info.get('columns', []))}")
                print(f"  Total Rows: {table_info.get('total_count', 0)}")
                print(f"  Sample Rows: {len(table_info.get('sample_rows', []))}")
                print()

    def _display_table_data(self, table_name: str, table_data: Dict[str, Any]):
        """Display specific table data."""
        if 'error' in table_data:
            self.display_error(table_data['error'])
            return

        if table_name not in table_data:
            self.display_error(f"Table '{table_name}' not found")
            return

        data = table_data[table_name]
        columns = data.get('columns', [])
        rows = data.get('rows', [])

        if HAS_RICH and console:
            table = Table(title=f"Table: {table_name}")

            # Add columns
            for col in columns:
                table.add_column(col, style="cyan")

            # Add rows
            for row in rows:
                # Convert all values to strings and truncate if too long
                str_row = [str(val)[:50] + "..." if len(str(val)) > 50 else str(val) for val in row]
                table.add_row(*str_row)

            console.print(table)
        else:
            print(f"\nTable: {table_name}")
            print("-" * 80)
            print(" | ".join(columns))
            print("-" * 80)
            for row in rows:
                print(" | ".join(str(val)[:30] for val in row))

    def _display_table_statistics(self, db_data: Dict[str, Any]):
        """Display table statistics."""
        if 'error' in db_data:
            self.display_error(db_data['error'])
            return

        total_tables = len(db_data)
        total_rows = sum(table_info.get('total_count', 0) for table_info in db_data.values())

        if HAS_RICH and console:
            stats_panel = Panel.fit(
                f"[bold]Database Statistics[/bold]\n"
                f"Total Tables: {total_tables}\n"
                f"Total Rows: {total_rows}\n"
                f"Average Rows per Table: {total_rows // total_tables if total_tables > 0 else 0}",
                title="📊 Statistics"
            )
            console.print(stats_panel)
        else:
            print("\nDatabase Statistics:")
            print(f"Total Tables: {total_tables}")
            print(f"Total Rows: {total_rows}")
            print(f"Average Rows per Table: {total_rows // total_tables if total_tables > 0 else 0}")

    def handle_user_data_management(self):
        """Handle user data management interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]User Data Management[/bold cyan]")
            console.print("1. List all users")
            console.print("2. View specific user")
            console.print("3. Edit user data")
            console.print("4. Reset user data")
            console.print("5. Delete user")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5"], default="0")
        else:
            print("\nUser Data Management")
            print("1. List all users")
            print("2. View specific user")
            print("3. Edit user data")
            print("4. Reset user data")
            print("5. Delete user")
            print("0. Back to main menu")

            choice = input("Select option (0-5): ").strip()

        if choice == "1":
            # List all users
            if HAS_RICH and console:
                with console.status("[bold green]Loading user data..."):
                    user_data = self.developer_tools.manage_user_data('list')
            else:
                print("Loading user data...")
                user_data = self.developer_tools.manage_user_data('list')

            self._display_user_list(user_data)

        elif choice == "2":
            # View specific user
            username = self.get_user_input("Enter username")
            if username:
                if HAS_RICH and console:
                    with console.status(f"[bold green]Loading data for {username}..."):
                        user_data = self.developer_tools.manage_user_data('view', username)
                else:
                    print(f"Loading data for {username}...")
                    user_data = self.developer_tools.manage_user_data('view', username)

                self._display_user_details(username, user_data)

        elif choice == "3":
            # Edit user data
            username = self.get_user_input("Enter username")
            if username:
                self._handle_user_edit(username)

        elif choice == "4":
            # Reset user data
            username = self.get_user_input("Enter username")
            if username and self.confirm_action(f"Reset all data for user '{username}'? This cannot be undone."):
                if HAS_RICH and console:
                    with console.status(f"[bold yellow]Resetting data for {username}..."):
                        result = self.developer_tools.manage_user_data('reset', username)
                else:
                    print(f"Resetting data for {username}...")
                    result = self.developer_tools.manage_user_data('reset', username)

                self.display_operation_result(result, f"Reset data for {username}")

        elif choice == "5":
            # Delete user
            username = self.get_user_input("Enter username")
            if username and self.confirm_action(f"Delete user '{username}'? This cannot be undone."):
                if HAS_RICH and console:
                    with console.status(f"[bold red]Deleting user {username}..."):
                        result = self.developer_tools.manage_user_data('delete', username)
                else:
                    print(f"Deleting user {username}...")
                    result = self.developer_tools.manage_user_data('delete', username)

                self.display_operation_result(result, f"Delete user {username}")

    def _display_user_list(self, user_data: Dict[str, Any]):
        """Display list of users."""
        if 'error' in user_data:
            self.display_error(user_data['error'])
            return

        users = user_data.get('users', [])
        total_count = user_data.get('total_count', 0)

        if HAS_RICH and console:
            table = Table(title=f"User List ({total_count} users)")
            table.add_column("Username", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Email", style="blue")
            table.add_column("Type", style="yellow")
            table.add_column("Trips", style="magenta")
            table.add_column("Distance", style="red")

            for user in users:
                user_type = "Admin" if user.get('is_admin') else ("Guest" if user.get('is_guest') else "User")
                # Handle None email values properly
                email = user.get('email') or 'N/A'
                table.add_row(
                    user.get('username', 'N/A'),
                    user.get('name', 'N/A'),
                    self.truncate_text(email, 30),
                    user_type,
                    str(user.get('total_trips', 0)),
                    f"{user.get('total_distance', 0):.1f} km"
                )

            console.print(table)
        else:
            print(f"\nUser List ({total_count} users):")
            print("-" * 80)
            for user in users:
                user_type = "Admin" if user.get('is_admin') else ("Guest" if user.get('is_guest') else "User")
                # Handle None email values properly
                email = user.get('email') or 'N/A'
                print(f"Username: {user.get('username', 'N/A')}")
                print(f"  Name: {user.get('name', 'N/A')}")
                print(f"  Email: {email}")
                print(f"  Type: {user_type}")
                print(f"  Trips: {user.get('total_trips', 0)}")
                print(f"  Distance: {user.get('total_distance', 0):.1f} km")
                print()

    def _display_user_details(self, username: str, user_data: Dict[str, Any]):
        """Display detailed user information."""
        if 'error' in user_data:
            self.display_error(user_data['error'])
            return

        user_info = user_data.get('user_data', {})

        if HAS_RICH and console:
            # Create a detailed view
            console.print(f"\n[bold cyan]User Details: {username}[/bold cyan]")

            # Handle None email values properly
            email = user_info.get('email') or 'N/A'

            # Basic info
            basic_panel = Panel.fit(
                f"[bold]Name:[/bold] {user_info.get('name', 'N/A')}\n"
                f"[bold]Email:[/bold] {email}\n"
                f"[bold]Admin:[/bold] {user_info.get('is_admin', False)}\n"
                f"[bold]Guest:[/bold] {user_info.get('is_guest', False)}",
                title="Basic Information"
            )
            console.print(basic_panel)

            # Statistics
            stats = user_info.get('stats', {})
            stats_panel = Panel.fit(
                f"[bold]Total Trips:[/bold] {stats.get('total_trips', 0)}\n"
                f"[bold]Total Distance:[/bold] {stats.get('total_distance', 0):.1f} km\n"
                f"[bold]CO2 Saved:[/bold] {stats.get('total_co2_saved', 0):.1f} kg\n"
                f"[bold]Calories:[/bold] {stats.get('total_calories', 0):.0f}",
                title="Statistics"
            )
            console.print(stats_panel)

        else:
            # Handle None email values properly
            email = user_info.get('email') or 'N/A'

            print(f"\nUser Details: {username}")
            print("=" * 50)
            print(f"Name: {user_info.get('name', 'N/A')}")
            print(f"Email: {email}")
            print(f"Admin: {user_info.get('is_admin', False)}")
            print(f"Guest: {user_info.get('is_guest', False)}")

            stats = user_info.get('stats', {})
            print(f"\nStatistics:")
            print(f"  Total Trips: {stats.get('total_trips', 0)}")
            print(f"  Total Distance: {stats.get('total_distance', 0):.1f} km")
            print(f"  CO2 Saved: {stats.get('total_co2_saved', 0):.1f} kg")
            print(f"  Calories: {stats.get('total_calories', 0):.0f}")

    def _handle_user_edit(self, username: str):
        """Handle user editing interface."""
        if HAS_RICH and console:
            console.print(f"\n[bold yellow]Edit User: {username}[/bold yellow]")
            console.print("Available fields to edit:")
            console.print("1. name")
            console.print("2. email")
            console.print("3. is_admin")
            console.print("4. is_guest")

            field = Prompt.ask("Enter field to edit", choices=["name", "email", "is_admin", "is_guest"])

            if field in ["is_admin", "is_guest"]:
                value = self.confirm_action(f"Set {field} to True?")
            else:
                value = self.get_user_input(f"Enter new value for {field}")
        else:
            print(f"\nEdit User: {username}")
            print("Available fields: name, email, is_admin, is_guest")
            field = input("Enter field to edit: ").strip()

            if field in ["is_admin", "is_guest"]:
                value = input(f"Set {field} to True? (y/N): ").strip().lower() == 'y'
            else:
                value = input(f"Enter new value for {field}: ").strip()

        if field:
            data = {field: value}
            if HAS_RICH and console:
                with console.status(f"[bold green]Updating {field} for {username}..."):
                    result = self.developer_tools.manage_user_data('edit', username, data)
            else:
                print(f"Updating {field} for {username}...")
                result = self.developer_tools.manage_user_data('edit', username, data)

            self.display_operation_result(result, f"Edit {field} for {username}")
