"""
EcoCycle - Cache Management UI Component
Handles cache operations and management.
"""
from typing import Dict, Any
from .base_ui import BaseUI, HAS_RICH, console, Table, Panel, Prompt


class CacheManagementUI(BaseUI):
    """UI component for cache management operations."""

    def handle_cache_management(self):
        """Handle cache management interface."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Cache Management[/bold cyan]")
            console.print("1. View all caches")
            console.print("2. View specific cache")
            console.print("3. Clear all caches")
            console.print("4. Clear specific cache")
            console.print("0. Back to main menu")

            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4"], default="0")
        else:
            print("\nCache Management")
            print("1. View all caches")
            print("2. View specific cache")
            print("3. Clear all caches")
            print("4. Clear specific cache")
            print("0. Back to main menu")

            choice = input("Select option (0-4): ").strip()

        if choice == "1":
            # View all caches
            if HAS_RICH and console:
                with console.status("[bold green]Loading cache data..."):
                    cache_data = self.developer_tools.manage_cache('view')
            else:
                print("Loading cache data...")
                cache_data = self.developer_tools.manage_cache('view')

            self._display_cache_overview(cache_data)

        elif choice == "2":
            # View specific cache
            cache_types = ['routes', 'weather', 'ai_routes', 'dependency']
            if HAS_RICH and console:
                cache_type = Prompt.ask("Select cache type", choices=cache_types)
            else:
                print("Available cache types:", ", ".join(cache_types))
                cache_type = input("Enter cache type: ").strip()

            if cache_type in cache_types:
                if HAS_RICH and console:
                    with console.status(f"[bold green]Loading {cache_type} cache..."):
                        cache_data = self.developer_tools.manage_cache('view', cache_type)
                else:
                    print(f"Loading {cache_type} cache...")
                    cache_data = self.developer_tools.manage_cache('view', cache_type)

                self._display_cache_details(cache_type, cache_data)

        elif choice == "3":
            # Clear all caches
            if self.confirm_action("Clear all caches? This cannot be undone."):
                if HAS_RICH and console:
                    with console.status("[bold yellow]Clearing all caches..."):
                        result = self.developer_tools.manage_cache('clear')
                else:
                    print("Clearing all caches...")
                    result = self.developer_tools.manage_cache('clear')

                self.display_operation_result(result, "Clear all caches")

        elif choice == "4":
            # Clear specific cache
            cache_types = ['routes', 'weather', 'ai_routes', 'dependency']
            if HAS_RICH and console:
                cache_type = Prompt.ask("Select cache type to clear", choices=cache_types)
            else:
                print("Available cache types:", ", ".join(cache_types))
                cache_type = input("Enter cache type to clear: ").strip()

            if cache_type in cache_types and self.confirm_action(f"Clear {cache_type} cache?"):
                if HAS_RICH and console:
                    with console.status(f"[bold yellow]Clearing {cache_type} cache..."):
                        result = self.developer_tools.manage_cache('clear', cache_type)
                else:
                    print(f"Clearing {cache_type} cache...")
                    result = self.developer_tools.manage_cache('clear', cache_type)

                self.display_operation_result(result, f"Clear {cache_type} cache")

    def _display_cache_overview(self, cache_data: Dict[str, Any]):
        """Display cache overview."""
        if HAS_RICH and console:
            table = Table(title="Cache Overview")
            table.add_column("Cache Type", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Size", style="yellow")
            table.add_column("Entries", style="magenta")
            table.add_column("Last Modified", style="blue")

            for cache_name, cache_info in cache_data.items():
                if cache_info.get('exists'):
                    status = "✅ Exists"
                    size = self.format_bytes(cache_info.get('size', 0))
                    entries = str(cache_info.get('entries', 'N/A'))
                    modified = self.format_timestamp(cache_info.get('modified', 'N/A'))
                else:
                    status = "❌ Missing"
                    size = "0 bytes"
                    entries = "0"
                    modified = "N/A"

                table.add_row(cache_name, status, size, entries, modified)

            console.print(table)
        else:
            print("\nCache Overview:")
            print("-" * 80)
            for cache_name, cache_info in cache_data.items():
                print(f"Cache: {cache_name}")
                if cache_info.get('exists'):
                    print(f"  Status: ✅ Exists")
                    print(f"  Size: {self.format_bytes(cache_info.get('size', 0))}")
                    print(f"  Entries: {cache_info.get('entries', 'N/A')}")
                    print(f"  Modified: {cache_info.get('modified', 'N/A')}")
                else:
                    print(f"  Status: ❌ Missing")
                print()

    def _display_cache_details(self, cache_type: str, cache_data: Dict[str, Any]):
        """Display detailed cache information."""
        cache_info = cache_data.get(cache_type, {})

        if 'error' in cache_info:
            self.display_error(cache_info['error'])
            return

        if HAS_RICH and console:
            console.print(f"\n[bold cyan]Cache Details: {cache_type}[/bold cyan]")

            if cache_info.get('exists'):
                details_panel = Panel.fit(
                    f"[bold]Size:[/bold] {self.format_bytes(cache_info.get('size', 0))}\n"
                    f"[bold]Entries:[/bold] {cache_info.get('entries', 'N/A')}\n"
                    f"[bold]Modified:[/bold] {self.format_timestamp(cache_info.get('modified', 'N/A'))}\n"
                    f"[bold]Sample Keys:[/bold] {', '.join(cache_info.get('sample_keys', [])[:5])}",
                    title=f"{cache_type} Cache"
                )
                console.print(details_panel)

                # Show sample entries if available
                sample_entries = cache_info.get('sample_entries', [])
                if sample_entries:
                    console.print(f"\n[bold yellow]Sample Entries (first 3):[/bold yellow]")
                    for i, entry in enumerate(sample_entries[:3], 1):
                        entry_panel = Panel.fit(
                            f"[bold]Key:[/bold] {entry.get('key', 'N/A')}\n"
                            f"[bold]Size:[/bold] {self.format_bytes(entry.get('size', 0))}\n"
                            f"[bold]Created:[/bold] {self.format_timestamp(entry.get('created', 'N/A'))}",
                            title=f"Entry {i}"
                        )
                        console.print(entry_panel)
            else:
                console.print(f"[red]Cache {cache_type} does not exist[/red]")
        else:
            print(f"\nCache Details: {cache_type}")
            print("=" * 50)
            if cache_info.get('exists'):
                print(f"Size: {self.format_bytes(cache_info.get('size', 0))}")
                print(f"Entries: {cache_info.get('entries', 'N/A')}")
                print(f"Modified: {cache_info.get('modified', 'N/A')}")
                print(f"Sample Keys: {', '.join(cache_info.get('sample_keys', [])[:5])}")
                
                sample_entries = cache_info.get('sample_entries', [])
                if sample_entries:
                    print("\nSample Entries:")
                    for i, entry in enumerate(sample_entries[:3], 1):
                        print(f"  Entry {i}:")
                        print(f"    Key: {entry.get('key', 'N/A')}")
                        print(f"    Size: {self.format_bytes(entry.get('size', 0))}")
                        print(f"    Created: {entry.get('created', 'N/A')}")
            else:
                print(f"Cache {cache_type} does not exist")

    def get_cache_statistics(self):
        """Get and display cache statistics."""
        if HAS_RICH and console:
            with console.status("[bold green]Calculating cache statistics..."):
                cache_data = self.developer_tools.manage_cache('view')
        else:
            print("Calculating cache statistics...")
            cache_data = self.developer_tools.manage_cache('view')

        self._display_cache_statistics(cache_data)

    def _display_cache_statistics(self, cache_data: Dict[str, Any]):
        """Display cache statistics."""
        total_caches = len(cache_data)
        existing_caches = len([c for c in cache_data.values() if c.get('exists')])
        total_size = sum(c.get('size', 0) for c in cache_data.values() if c.get('exists'))
        total_entries = sum(c.get('entries', 0) for c in cache_data.values() if c.get('exists', 0) and isinstance(c.get('entries'), int))

        if HAS_RICH and console:
            stats_panel = Panel.fit(
                f"[bold]Total Cache Types:[/bold] {total_caches}\n"
                f"[bold]Existing Caches:[/bold] {existing_caches}\n"
                f"[bold]Total Size:[/bold] {self.format_bytes(total_size)}\n"
                f"[bold]Total Entries:[/bold] {total_entries:,}\n"
                f"[bold]Cache Hit Rate:[/bold] {(existing_caches/total_caches*100):.1f}%" if total_caches > 0 else "[bold]Cache Hit Rate:[/bold] N/A",
                title="📊 Cache Statistics"
            )
            console.print(stats_panel)
        else:
            print("\nCache Statistics:")
            print(f"Total Cache Types: {total_caches}")
            print(f"Existing Caches: {existing_caches}")
            print(f"Total Size: {self.format_bytes(total_size)}")
            print(f"Total Entries: {total_entries:,}")
            if total_caches > 0:
                print(f"Cache Hit Rate: {(existing_caches/total_caches*100):.1f}%")

    def optimize_caches(self):
        """Optimize cache performance."""
        if HAS_RICH and console:
            console.print("\n[bold cyan]Cache Optimization[/bold cyan]")
            console.print("1. Remove expired entries")
            console.print("2. Compress cache files")
            console.print("3. Rebuild cache indexes")
            console.print("4. Full cache optimization")
            console.print("0. Back to cache menu")

            choice = Prompt.ask("Select optimization", choices=["0", "1", "2", "3", "4"], default="0")
        else:
            print("\nCache Optimization")
            print("1. Remove expired entries")
            print("2. Compress cache files")
            print("3. Rebuild cache indexes")
            print("4. Full cache optimization")
            print("0. Back to cache menu")

            choice = input("Select optimization (0-4): ").strip()

        if choice == "1":
            self._remove_expired_entries()
        elif choice == "2":
            self._compress_cache_files()
        elif choice == "3":
            self._rebuild_cache_indexes()
        elif choice == "4":
            self._full_cache_optimization()

    def _remove_expired_entries(self):
        """Remove expired cache entries."""
        if self.confirm_action("Remove expired cache entries?"):
            if HAS_RICH and console:
                with console.status("[bold yellow]Removing expired entries..."):
                    result = self.developer_tools.optimize_cache('remove_expired')
            else:
                print("Removing expired entries...")
                result = self.developer_tools.optimize_cache('remove_expired')

            self.display_operation_result(result, "Remove expired entries")

    def _compress_cache_files(self):
        """Compress cache files."""
        if self.confirm_action("Compress cache files? This may take some time."):
            if HAS_RICH and console:
                with console.status("[bold yellow]Compressing cache files..."):
                    result = self.developer_tools.optimize_cache('compress')
            else:
                print("Compressing cache files...")
                result = self.developer_tools.optimize_cache('compress')

            self.display_operation_result(result, "Compress cache files")

    def _rebuild_cache_indexes(self):
        """Rebuild cache indexes."""
        if self.confirm_action("Rebuild cache indexes?"):
            if HAS_RICH and console:
                with console.status("[bold yellow]Rebuilding cache indexes..."):
                    result = self.developer_tools.optimize_cache('rebuild_indexes')
            else:
                print("Rebuilding cache indexes...")
                result = self.developer_tools.optimize_cache('rebuild_indexes')

            self.display_operation_result(result, "Rebuild cache indexes")

    def _full_cache_optimization(self):
        """Perform full cache optimization."""
        if self.confirm_action("Perform full cache optimization? This will remove expired entries, compress files, and rebuild indexes."):
            if HAS_RICH and console:
                with console.status("[bold yellow]Performing full cache optimization..."):
                    result = self.developer_tools.optimize_cache('full')
            else:
                print("Performing full cache optimization...")
                result = self.developer_tools.optimize_cache('full')

            self.display_operation_result(result, "Full cache optimization")
