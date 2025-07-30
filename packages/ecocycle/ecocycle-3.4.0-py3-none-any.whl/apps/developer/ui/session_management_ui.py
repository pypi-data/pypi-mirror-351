"""
EcoCycle - Session Management UI Component
Handles session management functionality.
"""
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Table, Panel, Prompt


class SessionManagementUI(BaseUI):
    """UI component for session management."""

    def handle_session_management(self):
        """Handle session management interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Session Management[/bold cyan]")
            console.print("1. View session status")
            console.print("2. Clear user sessions")
            console.print("3. Extend developer session")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3"], default="0")
        else:
            print("\nSession Management")
            print("1. View session status")
            print("2. Clear user sessions")
            print("3. Extend developer session")
            print("0. Back to main menu")

            choice = input("Select option (0-3): ").strip()

        if choice == "1":
            # View session status
            if HAS_RICH and console:
                with console.status("[bold green]Loading session data..."):
                    session_data = self.developer_tools.manage_sessions('view')
            else:
                print("Loading session data...")
                session_data = self.developer_tools.manage_sessions('view')

            self._display_session_status(session_data)

        elif choice == "2":
            # Clear user sessions
            if self.confirm_action("Clear all user sessions? This will log out all users."):
                if HAS_RICH and console:
                    with console.status("[bold yellow]Clearing user sessions..."):
                        result = self.developer_tools.manage_sessions('clear_user_sessions')
                else:
                    print("Clearing user sessions...")
                    result = self.developer_tools.manage_sessions('clear_user_sessions')

                self.display_operation_result(result, "Clear user sessions")

        elif choice == "3":
            # Extend developer session
            if HAS_RICH and console:
                with console.status("[bold green]Extending developer session..."):
                    result = self.developer_tools.manage_sessions('extend_developer_session')
            else:
                print("Extending developer session...")
                result = self.developer_tools.manage_sessions('extend_developer_session')

            self.display_operation_result(result, "Extend developer session")

    def _display_session_status(self, session_data: Dict[str, Any]):
        """Display session status information."""
        dev_session = session_data.get('developer_session', {})
        user_sessions = session_data.get('user_sessions', {})

        if HAS_RICH and console:
            console.print("\n[bold cyan]Session Status[/bold cyan]")

            # Developer session
            dev_panel = Panel.fit(
                f"[bold]Username:[/bold] {dev_session.get('username', 'N/A')}\n"
                f"[bold]Authenticated:[/bold] {'✅ Yes' if dev_session.get('authenticated') else '❌ No'}\n"
                f"[bold]Session Start:[/bold] {self.format_timestamp(dev_session.get('session_start', 'N/A'))}\n"
                f"[bold]Time Remaining:[/bold] {dev_session.get('time_remaining', 'N/A')} seconds",
                title="Developer Session"
            )
            console.print(dev_panel)

            # User sessions
            if 'error' not in user_sessions:
                user_panel = Panel.fit(
                    f"[bold]Current User:[/bold] {user_sessions.get('current_user', 'None')}\n"
                    f"[bold]Login Time:[/bold] {self.format_timestamp(user_sessions.get('login_time', 'N/A'))}\n"
                    f"[bold]Last Activity:[/bold] {self.format_timestamp(user_sessions.get('last_activity', 'N/A'))}",
                    title="User Sessions"
                )
                console.print(user_panel)
            else:
                console.print(f"[yellow]User Sessions: {user_sessions['error']}[/yellow]")
        else:
            print("\nSession Status:")
            print("=" * 50)
            print("Developer Session:")
            print(f"  Username: {dev_session.get('username', 'N/A')}")
            print(f"  Authenticated: {'✅ Yes' if dev_session.get('authenticated') else '❌ No'}")
            print(f"  Session Start: {dev_session.get('session_start', 'N/A')}")
            print(f"  Time Remaining: {dev_session.get('time_remaining', 'N/A')} seconds")

            print("\nUser Sessions:")
            if 'error' not in user_sessions:
                print(f"  Current User: {user_sessions.get('current_user', 'None')}")
                print(f"  Login Time: {user_sessions.get('login_time', 'N/A')}")
                print(f"  Last Activity: {user_sessions.get('last_activity', 'N/A')}")
            else:
                print(f"  Error: {user_sessions['error']}")

    def handle_advanced_session_management(self):
        """Handle advanced session management features."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Advanced Session Management[/bold cyan]")
            console.print("1. View active sessions")
            console.print("2. View session history")
            console.print("3. Terminate specific session")
            console.print("4. Session statistics")
            console.print("0. Back to session menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4"], default="0")
        else:
            print("\nAdvanced Session Management")
            print("1. View active sessions")
            print("2. View session history")
            print("3. Terminate specific session")
            print("4. Session statistics")
            print("0. Back to session menu")

            choice = input("Select option (0-4): ").strip()

        if choice == "1":
            self._view_active_sessions()
        elif choice == "2":
            self._view_session_history()
        elif choice == "3":
            self._terminate_specific_session()
        elif choice == "4":
            self._view_session_statistics()

    def _view_active_sessions(self):
        """View all active sessions."""
        if HAS_RICH and console:
            with console.status("[bold green]Loading active sessions..."):
                session_data = self.developer_tools.get_active_sessions()
        else:
            print("Loading active sessions...")
            session_data = self.developer_tools.get_active_sessions()

        self._display_active_sessions(session_data)

    def _display_active_sessions(self, session_data: Dict[str, Any]):
        """Display active sessions."""
        if 'error' in session_data:
            self.display_error(session_data['error'])
            return

        sessions = session_data.get('active_sessions', [])

        if HAS_RICH and console:
            console.print("\n[bold cyan]Active Sessions[/bold cyan]")

            if sessions:
                table = Table(title=f"Active Sessions ({len(sessions)})")
                table.add_column("Session ID", style="cyan")
                table.add_column("Username", style="green")
                table.add_column("Start Time", style="yellow")
                table.add_column("Last Activity", style="blue")
                table.add_column("Status", style="magenta")

                for session in sessions:
                    table.add_row(
                        self.truncate_text(session.get('session_id', 'N/A'), 16) + "...",
                        session.get('username', 'N/A'),
                        self.format_timestamp(session.get('start_time', 'N/A')),
                        self.format_timestamp(session.get('last_activity', 'N/A')),
                        session.get('status', 'N/A')
                    )

                console.print(table)
            else:
                console.print("[yellow]No active sessions found[/yellow]")
        else:
            print("\nActive Sessions:")
            print("-" * 80)
            if sessions:
                for session in sessions:
                    print(f"Session ID: {session.get('session_id', 'N/A')}")
                    print(f"  Username: {session.get('username', 'N/A')}")
                    print(f"  Start Time: {session.get('start_time', 'N/A')}")
                    print(f"  Last Activity: {session.get('last_activity', 'N/A')}")
                    print(f"  Status: {session.get('status', 'N/A')}")
                    print()
            else:
                print("No active sessions found")

    def _view_session_history(self):
        """View session history."""
        self.display_info("🚧 Feature under development - Session history")

    def _terminate_specific_session(self):
        """Terminate a specific session."""
        session_id = self.get_user_input("Enter session ID to terminate")
        if session_id and self.confirm_action(f"Terminate session {session_id}?"):
            if HAS_RICH and console:
                with console.status(f"[bold yellow]Terminating session {session_id}..."):
                    result = self.developer_tools.terminate_session(session_id)
            else:
                print(f"Terminating session {session_id}...")
                result = self.developer_tools.terminate_session(session_id)

            self.display_operation_result(result, f"Terminate session {session_id}")

    def _view_session_statistics(self):
        """View session statistics."""
        self.display_info("🚧 Feature under development - Session statistics")
