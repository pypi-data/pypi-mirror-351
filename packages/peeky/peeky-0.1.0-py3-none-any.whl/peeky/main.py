#!/usr/bin/env python
"""
Peeky - A Minimal Port & Process Inspector

Main entry point for the Peeky CLI application.
"""

import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from peeky.cli.commands import app
from peeky.formatters.tables import COLORS
from peeky.formatters.ui import THEME, app_header, styled_panel


def main():
    """
    Main entry point function.
    """
    console = Console()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', '-h', action='store_true', help='Show help')
    parser.add_argument('--interactive', '-i', action='store_true', help='Start in interactive mode')
    
    # Only parse known args to allow the rest to be passed to Typer
    args, remaining = parser.parse_known_args()
    
    # If interactive mode is requested, launch it
    if args.interactive:
        try:
            from peeky.cli.interactive import launch_interactive
            launch_interactive()
            return
        except ImportError as e:
            console.print(f"Error: Could not load interactive mode: {e}", style="bold red")
            sys.exit(1)
    
    # If --help is specified and there are no other args, show our help
    if args.help and len(remaining) == 0:
        # Let Typer handle it
        sys.argv = [sys.argv[0], '--help']
        app()
        return
    
    # Display a welcome message when invoked with no arguments
    if len(sys.argv) == 1:
        console.print()
        
        # Create a styled header using the new UI framework
        header = app_header()
        console.print(header)
        
        # Create a commands table
        commands_table = Table(
            show_header=False, 
            box=None, 
            padding=(0, 2),
            title="Available Commands",
            title_style=THEME["section_title"],
        )
        commands_table.add_column("Command", style=f"{THEME['process']} bold")
        commands_table.add_column("Description", style=THEME["info"])
        
        commands_table.add_row("scan", "List open ports and processes")
        commands_table.add_row("conflicts", "Detect and display port conflicts")
        commands_table.add_row("stats", "View network statistics and summary")
        commands_table.add_row("kill", "Kill a process by port or PID")
        commands_table.add_row("clean", "Clean up idle or zombie port-bound processes")
        commands_table.add_row("export", "Export connection data to JSON or text")
        commands_table.add_row("secure", "Identify potential security risks")
        commands_table.add_row("whois", "Look up IP address or domain information")
        commands_table.add_row("--interactive", "Start in interactive mode (TUI)")
        
        # Create quick start panel
        quick_start = Text()
        quick_start.append("Try these commands:\n\n", style=THEME["section_title"])
        quick_start.append("  peeky scan", style=THEME["command"])
        quick_start.append(" - List all open ports\n", style=THEME["dim"])
        quick_start.append("  peeky --interactive", style=THEME["command"])
        quick_start.append(" - Start the interactive UI\n", style=THEME["dim"])
        quick_start.append("  peeky --help", style=THEME["command"])
        quick_start.append(" - Show detailed help\n", style=THEME["dim"])
        
        # Create and display panels
        commands_panel = styled_panel(
            commands_table,
            title="Commands",
            style="panel_border",
            padding=(1, 2)
        )
        
        quick_start_panel = styled_panel(
            quick_start,
            title="Quick Start",
            style="panel_border",
            padding=(1, 2)
        )
        
        console.print(commands_panel)
        console.print()
        console.print(quick_start_panel)
        console.print()
        sys.exit(0)
    
    # Otherwise, let Typer handle the commands
    app()


if __name__ == "__main__":
    main() 