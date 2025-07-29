"""
Interactive CLI mode for Peeky.

This module provides an interactive terminal-based interface for Peeky.
"""

import sys
import time
from typing import Dict, List, Optional, Callable
from rich.live import Live
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED

from peeky.formatters.ui import (
    THEME, 
    app_header, 
    styled_panel, 
    styled_prompt,
    styled_confirm,
    styled_input_panel,
    create_app_layout,
    print_styled_error,
    print_styled_info,
    print_styled_success,
)
from peeky.core.network import get_connection_with_process_info, detect_port_conflicts, calculate_network_stats
from peeky.core.process import find_idle_processes
from peeky.formatters.tables import (
    format_connections_table,
    format_conflicts_table,
    format_stats_table,
    format_idle_processes_table,
    print_table,
    COLORS,
)

# Global console instance
console = Console()

# Define the navigation state
navigation = {
    "current_screen": "main",  # Start on main screen
    "previous_screen": None,
    "running": True
}

# Define screen handlers
screen_handlers = {}


def launch_interactive():
    """
    Launch the interactive mode.
    This function is called from the main module when --interactive is provided.
    """
    try:
        # Start the interactive loop
        console.clear()
        console.print(app_header())
        console.print("Starting interactive mode...\n", style=THEME["info"])
        time.sleep(1)  # Give time to see the message
        
        # Start the main loop
        run_interactive()
    except KeyboardInterrupt:
        console.print("\n\nExiting Peeky interactive mode...", style=THEME["dim"])
        sys.exit(0)


def run_interactive():
    """
    Run the interactive UI.
    """
    # Define the screens
    register_screen_handler("main", main_screen)
    register_screen_handler("scan", scan_screen)
    register_screen_handler("conflicts", conflicts_screen)
    register_screen_handler("stats", stats_screen)
    register_screen_handler("clean", clean_screen)
    register_screen_handler("kill", kill_screen)
    register_screen_handler("secure", secure_screen)
    register_screen_handler("whois", whois_screen)
    register_screen_handler("export", export_screen)
    register_screen_handler("exit", exit_screen)
    
    # Main loop
    navigation["running"] = True
    navigation["current_screen"] = "main"
    
    while navigation["running"]:
        try:
            # Clear screen
            console.clear()
            
            # Get current screen handler
            screen = navigation["current_screen"]
            handler = screen_handlers.get(screen)
            
            if handler:
                # Run screen handler
                next_screen = handler()
                
                # Update navigation
                if next_screen:
                    navigation["previous_screen"] = screen
                    navigation["current_screen"] = next_screen
            else:
                # Unknown screen
                print_styled_error(f"Unknown screen: {screen}", "Navigation Error")
                styled_prompt("Press Enter to return to main screen...", "")
                navigation["current_screen"] = "main"
                
        except KeyboardInterrupt:
            # Handle Ctrl+C
            navigation["running"] = False
            console.print("\n\nExiting Peeky interactive mode...", style=THEME["dim"])
            sys.exit(0)
        except Exception as e:
            # Handle any other exceptions
            console.print(f"\n[bold red]Error:[/] {str(e)}")
            console.print_exception()
            styled_prompt("Press Enter to continue...", "")
            navigation["current_screen"] = "main"


def register_screen_handler(name: str, handler: Callable[[], str]) -> None:
    """
    Register a screen handler.
    
    Args:
        name: Screen name
        handler: Screen handler function
    """
    screen_handlers[name] = handler


# Main menu options
MENU_OPTIONS = [
    {"key": "1", "name": "Scan Ports", "desc": "List open ports with process information"},
    {"key": "2", "name": "Detect Conflicts", "desc": "Find port conflicts between processes"},
    {"key": "3", "name": "Network Stats", "desc": "View network statistics summary"},
    {"key": "4", "name": "Clean Idle Processes", "desc": "Identify and clean up idle processes"},
    {"key": "5", "name": "Kill Process", "desc": "Terminate a process by PID or port"},
    {"key": "6", "name": "Security Scan", "desc": "Check for security risks in network config"},
    {"key": "7", "name": "WHOIS Lookup", "desc": "Look up IP address or domain information"},
    {"key": "8", "name": "Export Data", "desc": "Export connection data to file"},
    {"key": "q", "name": "Quit", "desc": "Exit Peeky interactive mode"},
]


def create_menu_panel() -> Panel:
    """
    Create the main menu panel.
    
    Returns:
        Rich Panel object
    """
    content = Text()
    content.append("Select an option:\n\n", style=THEME["section_title"])
    
    for option in MENU_OPTIONS:
        # Highlight the key
        content.append(f"[{option['key']}] ", style=THEME["value_highlight"] + " bold")
        # Show the name
        content.append(f"{option['name']}", style=THEME["label"])
        # Show the description
        content.append(f" - {option['desc']}\n", style=THEME["dim"])
    
    panel = styled_panel(
        content,
        title="Peeky Menu",
        style="panel_border"
    )
    
    return panel


def scan_ports_screen(layout: Layout) -> None:
    """
    Show the scan ports screen.
    
    Args:
        layout: The main application layout
    """
    # Create input panel for filters
    filter_panel = styled_input_panel(
        "Filters (optional)",
        "Port: [leave empty for all] | Process name: [leave empty for all]",
        "Specify filters for the port scan or leave empty to see all connections."
    )
    
    # Update the layout
    layout["body"].update(filter_panel)
    
    # Get user input for filters
    port_filter = styled_prompt("Enter port number to filter (or press Enter for all)", "")
    process_filter = styled_prompt("Enter process name to filter (or press Enter for all)", "")
    show_command = styled_confirm("Show command that started the process?", False)
    
    # Convert port to int if provided
    port = int(port_filter) if port_filter and port_filter.isdigit() else None
    
    # Create "Loading" panel
    loading_panel = styled_panel(
        "Scanning ports...",
        title="Please Wait",
        style="info"
    )
    layout["body"].update(loading_panel)
    
    # Get connection data
    connections = get_connection_with_process_info(
        port=port,
        process_filter=process_filter if process_filter else None
    )
    
    # Format and display results
    if connections:
        table = format_connections_table(connections, show_command)
        result_panel = styled_panel(
            table,
            title="Scan Results",
            style="panel_border"
        )
    else:
        result_panel = styled_panel(
            "No connections found matching your criteria.",
            title="No Results",
            style="warning"
        )
    
    layout["body"].update(result_panel)
    
    # Wait for user to continue
    styled_prompt("Press Enter to return to the main menu", "")


def detect_conflicts_screen(layout: Layout) -> None:
    """
    Show the detect conflicts screen.
    
    Args:
        layout: The main application layout
    """
    # Create "Loading" panel
    loading_panel = styled_panel(
        "Detecting port conflicts...",
        title="Please Wait",
        style="info"
    )
    layout["body"].update(loading_panel)
    
    # Get conflicts data
    conflicts = detect_port_conflicts()
    
    # Format and display results
    if conflicts:
        table = format_conflicts_table(conflicts)
        result_panel = styled_panel(
            table,
            title="Port Conflicts Detected",
            style="panel_border"
        )
    else:
        result_panel = styled_panel(
            "No port conflicts detected. Your system is running smoothly!",
            title="No Conflicts",
            style="success"
        )
    
    layout["body"].update(result_panel)
    
    # Wait for user to continue
    styled_prompt("Press Enter to return to the main menu", "")


def network_stats_screen(layout: Layout) -> None:
    """
    Show the network stats screen.
    
    Args:
        layout: The main application layout
    """
    # Create "Loading" panel
    loading_panel = styled_panel(
        "Calculating network statistics...",
        title="Please Wait",
        style="info"
    )
    layout["body"].update(loading_panel)
    
    # Get stats data
    stats = calculate_network_stats()
    
    # Format and display results
    if stats["total_ports"] > 0:
        tables = format_stats_table(stats)
        
        # Create a Text object to hold all tables
        content = Text()
        
        # Add each table with some spacing
        for i, table in enumerate(tables):
            if i > 0:
                content.append("\n\n")
            layout["body"].update(styled_panel(
                table,
                title=f"Network Statistics {i+1}/{len(tables)}",
                style="panel_border"
            ))
            time.sleep(1)  # Pause to show each panel
    else:
        result_panel = styled_panel(
            "No open ports found. Network statistics unavailable.",
            title="No Data",
            style="warning"
        )
        layout["body"].update(result_panel)
    
    # Wait for user to continue
    styled_prompt("Press Enter to return to the main menu", "")


def clean_idle_screen(layout: Layout) -> None:
    """
    Show the clean idle processes screen.
    
    Args:
        layout: The main application layout
    """
    # Create "Loading" panel
    loading_panel = styled_panel(
        "Finding idle processes...",
        title="Please Wait",
        style="info"
    )
    layout["body"].update(loading_panel)
    
    # Get idle processes
    idle_processes = find_idle_processes()
    
    # Format and display results
    if idle_processes:
        tables = format_idle_processes_table(idle_processes)
        
        # Show the main table first
        layout["body"].update(styled_panel(
            tables[0],
            title="Idle Processes Found",
            style="warning"
        ))
        
        # Ask if user wants to see details
        if styled_confirm("Do you want to see detailed information for each process?", True):
            # Show detailed panels for each process
            for i, panel in enumerate(tables[1:], 1):
                layout["body"].update(panel)
                
                # If not the last panel, ask to continue
                if i < len(tables) - 1:
                    if not styled_confirm(f"View next process ({i}/{len(tables)-1})?", True):
                        break
        
        # Ask if user wants to clean up
        if styled_confirm("Do you want to clean up these idle processes?", False):
            from peeky.core.process import clean_idle_processes
            killed_processes = clean_idle_processes(force=False)
            
            if killed_processes:
                result = Text()
                result.append(f"Successfully cleaned up {len(killed_processes)} process(es):\n\n", 
                             style=THEME["success"])
                
                for proc in killed_processes:
                    result.append(f"• {proc.get('name', 'Unknown')} ", style=THEME["process"])
                    result.append(f"(PID: {proc.get('pid', 'N/A')})\n", style=THEME["pid"])
                
                layout["body"].update(styled_panel(
                    result,
                    title="Clean Complete",
                    style="success"
                ))
            else:
                layout["body"].update(styled_panel(
                    "No processes were cleaned up. They might be protected or require elevated permissions.",
                    title="Clean Failed",
                    style="error"
                ))
    else:
        layout["body"].update(styled_panel(
            "No idle processes found that could be cleaned up.",
            title="All Clear",
            style="success"
        ))
    
    # Wait for user to continue
    styled_prompt("Press Enter to return to the main menu", "")


def kill_process_screen(layout: Layout) -> None:
    """
    Show the kill process screen.
    
    Args:
        layout: The main application layout
    """
    # Create input panel
    input_panel = styled_input_panel(
        "Kill Process",
        "Enter PID or port number to kill",
        "You can enter either a process ID (PID) or a port number.\nPort numbers must be below 65536."
    )
    
    # Update the layout
    layout["body"].update(input_panel)
    
    # Get user input
    target = styled_prompt("Enter PID or port number to kill")
    
    if not target:
        return
    
    try:
        target_int = int(target)
    except ValueError:
        layout["body"].update(styled_panel(
            f"Error: '{target}' is not a valid PID or port number",
            title="Invalid Input",
            style="error"
        ))
        styled_prompt("Press Enter to return to the main menu", "")
        return
    
    # Check if risky and confirm
    from peeky.core.process import is_risky_process
    is_risky = False
    
    if target_int < 65536:  # Likely a port
        from peeky.core.network import get_connections
        connections = get_connections(port=target_int)
        pids = [conn.get("pid") for conn in connections if conn.get("pid")]
        
        for pid in pids:
            risky, reason = is_risky_process(pid)
            if risky:
                is_risky = True
                layout["body"].update(styled_panel(
                    f"Warning: {reason}",
                    title="Risky Operation",
                    style="warning"
                ))
                break
    else:  # Must be a PID
        risky, reason = is_risky_process(target_int)
        if risky:
            is_risky = True
            layout["body"].update(styled_panel(
                f"Warning: {reason}",
                title="Risky Operation",
                style="warning"
            ))
    
    # Ask for confirmation
    if is_risky:
        confirm = styled_confirm("Are you sure you want to continue with kill?", False)
        if not confirm:
            layout["body"].update(styled_panel(
                "Kill operation canceled.",
                title="Canceled",
                style="info"
            ))
            styled_prompt("Press Enter to return to the main menu", "")
            return
    
    # Proceed with kill
    from peeky.core.process import kill_process, kill_process_by_port
    
    # Create "Loading" panel
    loading_panel = styled_panel(
        "Attempting to kill process...",
        title="Please Wait",
        style="info"
    )
    layout["body"].update(loading_panel)
    
    success = False
    if target_int < 65536:  # Try as port first
        success = kill_process_by_port(target_int, force=False)
        if success:
            layout["body"].update(styled_panel(
                f"Successfully killed process using port {target_int}",
                title="Process Terminated",
                style="success"
            ))
        else:
            # Try as PID
            success = kill_process(target_int, force=False)
            if success:
                layout["body"].update(styled_panel(
                    f"Successfully killed process with PID {target_int}",
                    title="Process Terminated",
                    style="success"
                ))
            else:
                layout["body"].update(styled_panel(
                    f"Failed to kill: No process using port {target_int} or with PID {target_int}",
                    title="Kill Failed",
                    style="error"
                ))
    else:
        success = kill_process(target_int, force=False)
        if success:
            layout["body"].update(styled_panel(
                f"Successfully killed process with PID {target_int}",
                title="Process Terminated",
                style="success"
            ))
        else:
            layout["body"].update(styled_panel(
                f"Failed to kill process with PID {target_int}",
                title="Kill Failed",
                style="error"
            ))
    
    # Wait for user to continue
    styled_prompt("Press Enter to return to the main menu", "")


def security_scan_screen(layout: Layout) -> None:
    """
    Show the security scan screen.
    
    Args:
        layout: The main application layout
    """
    # Create "Loading" panel
    loading_panel = styled_panel(
        "Scanning for security risks...",
        title="Please Wait",
        style="info"
    )
    layout["body"].update(loading_panel)
    
    # Import here to avoid circular imports
    from peeky.core.secure import identify_exposed_ports, get_security_recommendations
    from peeky.formatters.security import format_security_table, format_recommendations
    
    # Get security data
    exposed_services = identify_exposed_ports()
    recommendations = get_security_recommendations(exposed_services)
    
    # Format and display results
    if exposed_services:
        # Show the security table
        table = format_security_table(exposed_services)
        layout["body"].update(styled_panel(
            table,
            title="Security Risks Detected",
            style="error"
        ))
        
        # Ask if user wants to see recommendations
        if styled_confirm("Do you want to see security recommendations?", True):
            panel = format_recommendations(recommendations)
            layout["body"].update(panel)
    else:
        layout["body"].update(styled_panel(
            "No security issues found. Your system appears to be configured securely.",
            title="Security Scan Results",
            style="success"
        ))
    
    # Wait for user to continue
    styled_prompt("Press Enter to return to the main menu", "")


def whois_lookup_screen(layout: Layout) -> None:
    """
    Show the WHOIS lookup screen.
    
    Args:
        layout: The main application layout
    """
    # Create input panel
    input_panel = styled_input_panel(
        "WHOIS Lookup",
        "Enter IP address or domain name",
        "Enter an IP address (e.g., 8.8.8.8) or a domain name (e.g., example.com)"
    )
    
    # Update the layout
    layout["body"].update(input_panel)
    
    # Get user input
    target = styled_prompt("Enter IP address or domain name")
    
    if not target:
        return
    
    # Show privacy warning
    layout["body"].update(styled_panel(
        "Note: This command makes external API calls to retrieve information.",
        title="Privacy Notice",
        style="warning"
    ))
    
    if not styled_confirm("Continue with external lookup?", True):
        return
    
    # Create "Loading" panel
    loading_panel = styled_panel(
        "Looking up information...",
        title="Please Wait",
        style="info"
    )
    layout["body"].update(loading_panel)
    
    # Import here to avoid circular imports
    from peeky.core.whois import perform_lookup
    from peeky.formatters.whois import format_whois_panel
    
    # Perform lookup
    data, error, lookup_type = perform_lookup(target)
    
    # Format and display results
    if error:
        layout["body"].update(styled_panel(
            f"Error: {error}",
            title="Lookup Failed",
            style="error"
        ))
    elif not data:
        layout["body"].update(styled_panel(
            "No information found for the provided target.",
            title="No Results",
            style="warning"
        ))
    else:
        panel = format_whois_panel(data, lookup_type)
        layout["body"].update(panel)
    
    # Wait for user to continue
    styled_prompt("Press Enter to return to the main menu", "")


def export_data_screen(layout: Layout) -> None:
    """
    Show the export data screen.
    
    Args:
        layout: The main application layout
    """
    # Create input panel for export options
    export_panel = styled_input_panel(
        "Export Options",
        "Format: [json/text] | Filename: [leave empty for stdout]",
        "Specify export format and optional filename."
    )
    
    # Update the layout
    layout["body"].update(export_panel)
    
    # Get user input for export options
    format_type = styled_prompt("Export format", "text", choices=["text", "json"])
    output_file = styled_prompt("Output file (or press Enter for console output)", "")
    
    # Get filters
    port_filter = styled_prompt("Enter port number to filter (or press Enter for all)", "")
    process_filter = styled_prompt("Enter process name to filter (or press Enter for all)", "")
    
    # Convert port to int if provided
    port = int(port_filter) if port_filter and port_filter.isdigit() else None
    
    # Create "Loading" panel
    loading_panel = styled_panel(
        "Preparing export data...",
        title="Please Wait",
        style="info"
    )
    layout["body"].update(loading_panel)
    
    # Get connection data
    from peeky.core.network import get_connection_with_process_info
    connections = get_connection_with_process_info(
        port=port,
        process_filter=process_filter if process_filter else None
    )
    
    # Format and export data
    if not connections:
        layout["body"].update(styled_panel(
            "No connections found matching your criteria.",
            title="No Data",
            style="warning"
        ))
    else:
        # Import export function
        from peeky.formatters.export import write_export
        
        try:
            # If stdout, capture the output
            if not output_file:
                import io
                import sys
                
                # Redirect stdout temporarily
                old_stdout = sys.stdout
                new_stdout = io.StringIO()
                sys.stdout = new_stdout
                
                # Export data
                write_export(connections, None, format_type)
                
                # Get the output and restore stdout
                export_output = new_stdout.getvalue()
                sys.stdout = old_stdout
                
                # Display the output
                layout["body"].update(styled_panel(
                    export_output,
                    title="Export Result",
                    style="info"
                ))
            else:
                # Export to file
                write_export(connections, output_file, format_type)
                
                layout["body"].update(styled_panel(
                    f"Data successfully exported to '{output_file}'",
                    title="Export Complete",
                    style="success"
                ))
        except Exception as e:
            layout["body"].update(styled_panel(
                f"Error exporting data: {str(e)}",
                title="Export Failed",
                style="error"
            ))
    
    # Wait for user to continue
    styled_prompt("Press Enter to return to the main menu", "")


def main_screen() -> str:
    """
    Show the main screen.
    
    Returns:
        Next screen name
    """
    # Show the menu
    layout = create_app_layout()
    layout["body"].update(create_menu_panel())
    
    # Get user choice
    choice = styled_prompt("Enter your choice", "")
    
    if choice == "q":
        return "exit"
    elif choice == "1":
        scan_ports_screen(layout)
        return "main"
    elif choice == "2":
        detect_conflicts_screen(layout)
        return "main"
    elif choice == "3":
        network_stats_screen(layout)
        return "main"
    elif choice == "4":
        clean_idle_screen(layout)
        return "main"
    elif choice == "5":
        kill_process_screen(layout)
        return "main"
    elif choice == "6":
        security_scan_screen(layout)
        return "main"
    elif choice == "7":
        whois_lookup_screen(layout)
        return "main"
    elif choice == "8":
        export_data_screen(layout)
        return "main"
    else:
        return "main"


def scan_screen() -> str:
    """
    Show the scan screen.
    
    Returns:
        Next screen name
    """
    scan_ports_screen(create_app_layout())
    return "main"


def conflicts_screen() -> str:
    """
    Show the conflicts screen.
    
    Returns:
        Next screen name
    """
    detect_conflicts_screen(create_app_layout())
    return "main"


def stats_screen() -> str:
    """
    Show the stats screen.
    
    Returns:
        Next screen name
    """
    network_stats_screen(create_app_layout())
    return "main"


def clean_screen() -> str:
    """
    Show the clean screen.
    
    Returns:
        Next screen name
    """
    clean_idle_screen(create_app_layout())
    return "main"


def kill_screen() -> str:
    """
    Show the kill screen.
    
    Returns:
        Next screen name
    """
    kill_process_screen(create_app_layout())
    return "main"


def secure_screen() -> str:
    """
    Show the secure screen.
    
    Returns:
        Next screen name
    """
    security_scan_screen(create_app_layout())
    return "main"


def whois_screen() -> str:
    """
    Show the whois screen.
    
    Returns:
        Next screen name
    """
    whois_lookup_screen(create_app_layout())
    return "main"


def export_screen() -> str:
    """
    Show the export screen.
    
    Returns:
        Next screen name
    """
    export_data_screen(create_app_layout())
    return "main"


def exit_screen() -> str:
    """
    Show the exit screen.
    
    Returns:
        Next screen name
    """
    # Show goodbye message
    console.print()
    console.print(styled_panel(
        "Thank you for using Peeky!",
        title="Goodbye",
        style="info"
    ))
    return "exit" 