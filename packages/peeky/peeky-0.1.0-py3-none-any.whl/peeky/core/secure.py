"""
Security operations for Peeky.

This module provides functions for security scanning and analysis.
"""

import socket
from typing import Dict, List, Any, Tuple, Optional

from peeky.core.network import get_connections

# Define common vulnerable services and their default ports
VULNERABLE_SERVICES = {
    21: {"name": "FTP", "risk": "high", "description": "Unencrypted file transfer protocol"},
    22: {"name": "SSH", "risk": "medium", "description": "Secure Shell - ensure using latest version"},
    23: {"name": "Telnet", "risk": "critical", "description": "Unencrypted remote access protocol"},
    25: {"name": "SMTP", "risk": "medium", "description": "Email transfer protocol"},
    53: {"name": "DNS", "risk": "medium", "description": "Domain Name System"},
    80: {"name": "HTTP", "risk": "medium", "description": "Unencrypted web server"},
    110: {"name": "POP3", "risk": "high", "description": "Unencrypted email retrieval"},
    135: {"name": "RPC", "risk": "high", "description": "Windows RPC service"},
    137: {"name": "NetBIOS", "risk": "high", "description": "NetBIOS Name Service"},
    138: {"name": "NetBIOS", "risk": "high", "description": "NetBIOS Datagram Service"},
    139: {"name": "NetBIOS", "risk": "high", "description": "NetBIOS Session Service"},
    445: {"name": "SMB", "risk": "high", "description": "File sharing service"},
    1433: {"name": "MSSQL", "risk": "high", "description": "Microsoft SQL Server"},
    1521: {"name": "Oracle", "risk": "high", "description": "Oracle Database"},
    3306: {"name": "MySQL", "risk": "high", "description": "MySQL Database"},
    3389: {"name": "RDP", "risk": "high", "description": "Remote Desktop Protocol"},
    5432: {"name": "PostgreSQL", "risk": "high", "description": "PostgreSQL Database"},
    5900: {"name": "VNC", "risk": "high", "description": "Virtual Network Computing"},
    8080: {"name": "HTTP-ALT", "risk": "medium", "description": "Alternative HTTP port"},
}

def identify_exposed_ports() -> List[Dict[str, Any]]:
    """
    Identify potentially exposed or vulnerable ports.
    
    Returns:
        List of dictionaries with exposed port information
    """
    connections = get_connections()
    
    # Find listening sockets that may be exposed
    exposed_services = []
    for conn in connections:
        if conn["status"] == "LISTEN" and conn["protocol"] == socket.SOCK_STREAM:
            port = conn["local_port"]
            local_addr = conn["local_address"]
            
            # Skip if not externally accessible
            if local_addr in ("127.0.0.1", "::1", "localhost"):
                continue
                
            # Check if this is a known vulnerable service
            service_info = VULNERABLE_SERVICES.get(port, {
                "name": "Unknown",
                "risk": "low",
                "description": "Unknown service"
            })
            
            # Try to get process info
            process_name = "Unknown"
            pid = conn["pid"]
            if pid:
                try:
                    import psutil
                    process = psutil.Process(pid)
                    process_name = process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Create exposed service entry
            exposed = {
                "port": port,
                "address": local_addr,
                "service": service_info["name"],
                "risk": service_info["risk"],
                "description": service_info["description"],
                "process": process_name,
                "pid": pid
            }
            
            exposed_services.append(exposed)
    
    return exposed_services


def get_security_recommendations(exposed_services: List[Dict[str, Any]]) -> List[str]:
    """
    Generate security recommendations based on exposed services.
    
    Args:
        exposed_services: List of exposed service dictionaries from identify_exposed_ports
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Check for high-risk services
    high_risk_services = [s for s in exposed_services if s["risk"] in ("high", "critical")]
    if high_risk_services:
        recommendations.append(
            "High-risk services detected: " + 
            ", ".join(f"{s['service']} (port {s['port']})" for s in high_risk_services)
        )
        recommendations.append(
            "Consider using a firewall to restrict access to these services or disable them if not needed."
        )
    
    # Check for unencrypted services
    unencrypted = [s for s in exposed_services if s["service"] in ("HTTP", "FTP", "Telnet", "POP3")]
    if unencrypted:
        recommendations.append(
            "Unencrypted services detected: " + 
            ", ".join(f"{s['service']} (port {s['port']})" for s in unencrypted)
        )
        recommendations.append(
            "Consider replacing these with encrypted alternatives (HTTPS, SFTP, SSH, POP3S)."
        )
    
    # Check for database services
    databases = [s for s in exposed_services if s["service"] in ("MySQL", "PostgreSQL", "MSSQL", "Oracle")]
    if databases:
        recommendations.append(
            "Database services are exposed: " + 
            ", ".join(f"{s['service']} (port {s['port']})" for s in databases)
        )
        recommendations.append(
            "Restrict database access using firewall rules, bind to localhost, or use VPN for remote access."
        )
    
    # Check for remote access services
    remote_access = [s for s in exposed_services if s["service"] in ("SSH", "RDP", "VNC")]
    if remote_access:
        recommendations.append(
            "Remote access services are exposed: " + 
            ", ".join(f"{s['service']} (port {s['port']})" for s in remote_access)
        )
        recommendations.append(
            "Use strong authentication, key-based authentication for SSH, and consider IP restrictions."
        )
    
    # General recommendations
    if exposed_services:
        recommendations.append(
            "Consider setting up a host-based firewall to restrict access to necessary services only."
        )
        recommendations.append(
            "Regularly update and patch all services to protect against known vulnerabilities."
        )
    else:
        recommendations.append(
            "No significant security issues detected. Continue to monitor your system regularly."
        )
    
    return recommendations 