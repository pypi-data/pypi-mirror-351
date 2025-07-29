#!/usr/bin/env python3
"""
VibeOps CLI - Configure Cursor to use VibeOps MCP server
"""

import os
import json
import click
import platform
import requests
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

console = Console()

def get_cursor_config_dir():
    """Get the Cursor configuration directory based on the operating system"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / ".cursor"
    elif system == "Windows":
        return Path.home() / ".cursor"
    elif system == "Linux":
        return Path.home() / ".cursor"
    else:
        console.print(f"[red]Unsupported operating system: {system}[/red]")
        return None

def test_server_connection(server_url: str) -> bool:
    """Test connection to VibeOps server using SSE endpoint"""
    try:
        # Test the SSE endpoint with Accept: text/event-stream header
        response = requests.get(
            f"{server_url}/sse",
            headers={"Accept": "text/event-stream"},
            timeout=5,
            stream=True
        )
        # For SSE, we expect 200 status and the response should start streaming
        return response.status_code == 200 and 'text/event-stream' in response.headers.get('content-type', '')
    except Exception:
        return False

@click.group()
def cli():
    """VibeOps CLI - Configure Cursor for DevOps automation"""
    pass

@cli.command()
@click.option('--server-url', help='URL of remote VibeOps MCP server', default='http://20.83.174.151:8000')
def init(server_url):
    """Initialize VibeOps MCP configuration for Cursor"""
    
    # Test server connection first
    if not test_server_connection(server_url):
        click.echo(f"❌ Cannot connect to VibeOps server at {server_url}")
        click.echo("Please check if the server is running and accessible.")
        return
    
    click.echo(f"✅ Connected to VibeOps server at {server_url}")
    
    # Create Cursor MCP configuration directory
    cursor_dir = os.path.expanduser("~/.cursor")
    os.makedirs(cursor_dir, exist_ok=True)
    
    config_path = os.path.join(cursor_dir, "mcp.json")
    
    # Load existing config or create new one
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}
    
    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Configure VibeOps MCP server using SSE transport
    config["mcpServers"]["vibeops"] = {
        "url": f"{server_url}/sse",
        "env": {
            "MCP_SERVER_URL": server_url
        }
    }
    
    # Write the configuration
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo(f"✅ VibeOps MCP configuration written to {config_path}")
    click.echo("🔄 Please restart Cursor to load the new configuration")
    
    # Display the configuration
    click.echo("\n📋 Configuration added:")
    click.echo(f"   Server URL: {server_url}/sse")
    click.echo(f"   Transport: SSE (Server-Sent Events)")
    click.echo(f"   Tools: deploy_application, check_deployment_logs, get_logs_by_app, redeploy_on_changes, list_all_deployments")

@cli.command()
def status():
    """Check VibeOps MCP configuration status"""
    
    cursor_dir = get_cursor_config_dir()
    if not cursor_dir:
        return
    
    config_path = cursor_dir / "mcp.json"
    
    if not config_path.exists():
        console.print("[red]❌ No MCP configuration found[/red]")
        console.print("Run 'vibeops init' to set up the configuration")
        return
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "mcpServers" not in config or "vibeops" not in config["mcpServers"]:
            console.print("[red]❌ VibeOps not configured in MCP[/red]")
            console.print("Run 'vibeops init' to set up the configuration")
            return
        
        vibeops_config = config["mcpServers"]["vibeops"]
        server_url = vibeops_config.get("url", "").replace("/sse", "")
        
        console.print("[green]✅ VibeOps MCP configuration found[/green]")
        console.print(f"Server URL: {vibeops_config.get('url', 'Not configured')}")
        
        # Test server connection
        if server_url and test_server_connection(server_url):
            console.print("[green]✅ Server is accessible[/green]")
        else:
            console.print("[red]❌ Server is not accessible[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Error reading configuration: {e}[/red]")

@cli.command()
@click.argument('server_url')
def test_server(server_url):
    """Test connection to a VibeOps server"""
    
    console.print(f"Testing connection to {server_url}...")
    
    if test_server_connection(server_url):
        console.print("[green]✅ Server is accessible[/green]")
        console.print(f"SSE endpoint: {server_url}/sse")
    else:
        console.print("[red]❌ Cannot connect to server[/red]")
        console.print("Please check:")
        console.print("- Server is running")
        console.print("- URL is correct")
        console.print("- Network connectivity")
        console.print("- Firewall settings")

if __name__ == "__main__":
    cli() 